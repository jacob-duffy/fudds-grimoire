"""Item rolling engine — filter catalog items and randomly sample one."""

import random
import re

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import LootTableLoader
from grimoire.models.constants import RARITY_RANK, ItemType

# Re-export RARITY_RANK so existing callers that import it from this module
# continue to work without modification.
__all__ = [
    "RARITY_RANK",
    "roll_item",
    "roll_table",
    "parse_rolls",
    "filter_items",
    "load_all_items",
    "roll_currency",
]

ITEM_TYPES = list(ItemType)

# Defaults used by the currency shortcut when no wealth range is specified.
CURRENCY_DEFAULT_MIN: float = 0.0
CURRENCY_DEFAULT_MAX: float = 500.0


def load_all_items(loader: ItemCatalogLoader) -> list[dict]:
    """Load every item from every catalog file, deduplicating by file path.

    Each returned dict has an ``_id`` key injected with the item's catalog ID
    when not already present.  Files that map to the same path (e.g. ``wand``
    and ``staff`` both resolve to ``wondrous.yml``) are read only once.
    """
    seen_files: set = set()
    items: list[dict] = []

    for item_type in ITEM_TYPES:
        path = loader.file_for_type(item_type)
        if path in seen_files:
            continue
        seen_files.add(path)

        catalog = loader.load(item_type)
        for item_id, item_data in catalog["items"].items():
            if not isinstance(item_data, dict):
                continue
            entry = dict(item_data)
            entry.setdefault("_id", item_id)
            items.append(entry)

    return items


def filter_items(
    items: list[dict],
    rarities: list[str] | None = None,
    rarity_mode: str = "manual",
    rarity_ref: str | None = None,
    types: list[str] | None = None,
    types_mode: str = "include",
    wealth_min: float | None = None,
    wealth_max: float | None = None,
) -> list[dict]:
    """Return the subset of *items* that passes all active filters.

    Parameters
    ----------
    rarities:
        Used when *rarity_mode* is ``"manual"``.  Only items whose
        ``rarity`` is in this list are kept.  Pass ``None`` or ``[]`` to
        skip rarity filtering entirely.
    rarity_mode:
        Controls how the rarity filter is applied:

        * ``"manual"`` — keep items whose rarity is in *rarities*.
        * ``"eq"``  — rarity == *rarity_ref*
        * ``"geq"`` — rarity >= *rarity_ref* (by ``RARITY_RANK``)
        * ``"gt"``  — rarity >  *rarity_ref*
        * ``"leq"`` — rarity <= *rarity_ref*
        * ``"lt"``  — rarity <  *rarity_ref*

        Comparator modes exclude items whose rarity is not present in
        ``RARITY_RANK`` (e.g. ``"varies"``).
    rarity_ref:
        Reference rarity string used by comparator modes.  Ignored when
        *rarity_mode* is ``"manual"``.
    types:
        When non-empty, filtered by ``type`` according to *types_mode*.
        Pass ``None`` or ``[]`` to skip type filtering.
    types_mode:
        ``"include"`` — keep only items whose type *is* in *types*.
        ``"exclude"`` — remove items whose type *is* in *types*.
    wealth_min / wealth_max:
        When set, items with a ``value_gp`` field outside the range are
        removed.  Items that have *no* ``value_gp`` field always pass.
    """
    result = items

    if rarity_mode == "manual":
        if rarities:
            result = [i for i in result if i.get("rarity") in rarities]
    elif rarity_ref is not None:
        if rarity_ref not in RARITY_RANK:
            # Reference rarity has no rank (e.g. "varies") — nothing passes.
            result = []
        else:
            ref_rank = RARITY_RANK[rarity_ref]
            ops = {
                "eq": lambda r: r == ref_rank,
                "geq": lambda r: r >= ref_rank,
                "gt": lambda r: r > ref_rank,
                "leq": lambda r: r <= ref_rank,
                "lt": lambda r: r < ref_rank,
            }
            op = ops.get(rarity_mode)
            if op:
                result = [
                    i
                    for i in result
                    if i.get("rarity") in RARITY_RANK and op(RARITY_RANK[i["rarity"]])
                ]

    if types:
        if types_mode == "include":
            result = [i for i in result if i.get("type") in types]
        else:
            result = [i for i in result if i.get("type") not in types]

    if wealth_min is not None:
        result = [
            i
            for i in result
            if i.get("value_gp") is None or i["value_gp"] >= wealth_min
        ]

    if wealth_max is not None:
        result = [
            i
            for i in result
            if i.get("value_gp") is None or i["value_gp"] <= wealth_max
        ]

    return result


def roll_currency(
    wealth_min: float,
    wealth_max: float,
    rng: random.Random | None = None,
) -> dict:
    """Return a synthetic currency result within *wealth_min*–*wealth_max* gp.

    The amount is rounded to two decimal places.  When min equals max the
    exact value is returned.
    """
    _rng = rng or random.Random()
    if wealth_min == wealth_max:
        amount: float = wealth_min
    else:
        amount = round(_rng.uniform(wealth_min, wealth_max), 2)

    int_amount = int(amount) if amount == int(amount) else amount
    return {
        "_id": "_currency_roll",
        "name": f"{int_amount} gp",
        "type": "currency",
        "rarity": "common",
        "value_gp": amount,
    }


def roll_item(
    loader: ItemCatalogLoader,
    rarities: list[str] | None = None,
    rarity_mode: str = "manual",
    rarity_ref: str | None = None,
    types: list[str] | None = None,
    types_mode: str = "include",
    wealth_min: float | None = None,
    wealth_max: float | None = None,
    rng: random.Random | None = None,
) -> dict | None:
    """Sample one item that matches all active filters, or ``None`` if none match.

    Special case — currency-only rolls
    -----------------------------------
    When *types* is exactly ``["currency"]`` in ``"include"`` mode, a
    synthetic GP amount is generated without consulting the catalog.  Rarity
    is irrelevant for currency and is ignored.  If no wealth bounds are
    supplied, defaults of ``CURRENCY_DEFAULT_MIN``/``CURRENCY_DEFAULT_MAX``
    (0–500 gp) are used.

    Parameters
    ----------
    loader:
        Catalog loader used to enumerate available items.
    rarities:
        List of rarity strings to include (used when *rarity_mode* is
        ``"manual"``).  ``None``/empty = all rarities.
    rarity_mode:
        ``"manual"``, ``"eq"``, ``"geq"``, ``"gt"``, ``"leq"``, or ``"lt"``.
    rarity_ref:
        Reference rarity for comparator modes.
    types:
        List of item type strings to filter on.  ``None``/empty = all types.
    types_mode:
        ``"include"`` or ``"exclude"``.
    wealth_min / wealth_max:
        GP range filter.  ``None`` = no bound (currency rolls default to
        ``CURRENCY_DEFAULT_MIN`` / ``CURRENCY_DEFAULT_MAX``).
    rng:
        Optional seeded :class:`random.Random` instance for reproducible tests.
    """
    _rng = rng or random.Random()

    # Currency-only shortcut: always generate a GP value — rarity is skipped,
    # and wealth range defaults to 0–500 when not specified.
    if types and set(types) == {"currency"} and types_mode == "include":
        _min = wealth_min if wealth_min is not None else CURRENCY_DEFAULT_MIN
        _max = wealth_max if wealth_max is not None else CURRENCY_DEFAULT_MAX
        return roll_currency(_min, _max, _rng)

    all_items = load_all_items(loader)
    candidates = filter_items(
        all_items,
        rarities=rarities,
        rarity_mode=rarity_mode,
        rarity_ref=rarity_ref,
        types=types,
        types_mode=types_mode,
        wealth_min=wealth_min,
        wealth_max=wealth_max,
    )

    if not candidates:
        return None

    return _rng.choice(candidates)


# ---------------------------------------------------------------------------
# Loot-table rolling
# ---------------------------------------------------------------------------

_DICE_RE = re.compile(r"^(\d+)d(\d+)(?:\+(\d+))?$")


def parse_rolls(rolls_field: int | str | None, rng: random.Random | None = None) -> int:
    """Evaluate a table's ``rolls`` field and return the number of rolls to make.

    *rolls_field* may be:
    - ``None`` or missing → returns 1.
    - a positive integer → returned directly.
    - a dice string such as ``"1d4"`` or ``"2d6+1"`` → rolled and returned.

    Raises :class:`ValueError` for unrecognisable strings.
    """
    if rolls_field is None:
        return 1
    if isinstance(rolls_field, int):
        return max(1, rolls_field)

    match = _DICE_RE.match(str(rolls_field).strip())
    if not match:
        raise ValueError(f"Cannot parse rolls expression: {rolls_field!r}")

    _rng = rng or random.Random()
    num_dice = int(match.group(1))
    die_faces = int(match.group(2))
    modifier = int(match.group(3) or 0)
    result = sum(_rng.randint(1, die_faces) for _ in range(num_dice)) + modifier
    return max(1, result)


def roll_table(
    table: dict,
    catalog_loader: ItemCatalogLoader | None = None,
    table_loader: LootTableLoader | None = None,
    rng: random.Random | None = None,
    _visited: frozenset[str] | None = None,
) -> list[dict]:
    """Roll on a loot table and return a list of resolved item dicts.

    The number of rolls is determined by the table's ``rolls`` field (defaults
    to 1).  Each roll independently picks a weighted entry from ``entries``.

    Entry resolution
    ----------------
    ``item``       — inline dict is returned directly; ``_id`` is synthesised
                     from the item's ``name`` when absent.
    ``item_ref``   — looked up across all catalog files; falls back to a stub
                     dict ``{"_id": id, "name": id}`` when not found or when
                     no *catalog_loader* is provided.
    ``reference``  — when *table_loader* is provided the referenced table is
                     loaded and rolled recursively (cycles are detected via
                     *_visited* and fall back to a stub).  Without a loader a
                     stub ``{"_id": "_ref:<id>", "name": "[Table: <id>]"}`` is
                     returned.

    Returns an empty list when the table has no entries.
    """
    _rng = rng or random.Random()
    entries = table.get("entries", [])
    if not entries:
        return []

    # Build item index lazily only if needed.
    _item_index: dict[str, dict] | None = None

    def _get_index() -> dict[str, dict]:
        nonlocal _item_index
        if _item_index is None and catalog_loader is not None:
            _item_index = {
                item["_id"]: item
                for item in load_all_items(catalog_loader)
                if "_id" in item
            }
        return _item_index or {}

    weights = [max(int(entry.get("weight", 1)), 1) for entry in entries]
    num_rolls = parse_rolls(table.get("rolls"), _rng)

    results: list[dict] = []
    for _ in range(num_rolls):
        entry = _rng.choices(entries, weights=weights, k=1)[0]

        if "item" in entry:
            item = dict(entry["item"])
            item.setdefault("_id", item.get("name", "inline_item"))
            results.append(item)

        elif "item_ref" in entry:
            item_id = str(entry["item_ref"])
            found = _get_index().get(item_id)
            if found is not None:
                results.append(found)
            else:
                results.append({"_id": item_id, "name": item_id})

        elif "reference" in entry:
            ref_id = str(entry["reference"])
            _vis = _visited or frozenset()
            if table_loader is not None and ref_id not in _vis:
                sub_table = table_loader.find_by_id(ref_id)
                if sub_table is not None:
                    sub_results = roll_table(
                        sub_table,
                        catalog_loader=catalog_loader,
                        table_loader=table_loader,
                        rng=_rng,
                        _visited=_vis | {ref_id},
                    )
                    results.extend(sub_results)
                    continue
            # No loader, table not found, or cycle — return stub.
            results.append({"_id": f"_ref:{ref_id}", "name": f"[Table: {ref_id}]"})

        else:
            # Malformed entry — skip silently.
            pass

    return results
