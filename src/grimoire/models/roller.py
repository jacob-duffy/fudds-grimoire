"""Item rolling engine — filter catalog items and randomly sample one."""

import random

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.models.item import ITEM_TYPES

# Ordinal rank for each named rarity.  "varies" is intentionally absent
# because it has no meaningful position in the scale.
RARITY_RANK: dict[str, int] = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "very rare": 3,
    "legendary": 4,
    "artifact": 5,
}

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
