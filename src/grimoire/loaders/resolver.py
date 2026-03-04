"""Loot-table entry resolution for Fudd's Grimoire.

Provides :func:`resolve_table_entries`, a pure function that recursively
expands a table's raw ``entries`` list — following ``item_ref`` and
``reference`` links — into a flat list of resolved item dicts, each
augmented with a ``_weight`` key for weighted random selection.

Extracting this logic from the UI layer keeps the screen thin and makes the
resolution algorithm independently testable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grimoire.loaders.tables import LootTableLoader


def resolve_table_entries(
    entries: list[dict],
    item_index: dict[str, dict],
    table_loader: "LootTableLoader",
    visited: frozenset[str] | None = None,
    parent_weight: int = 1,
) -> list[dict]:
    """Recursively resolve *entries* into a flat list of item dicts.

    Parameters
    ----------
    entries:
        Raw entry dicts from a table's ``entries`` list.
    item_index:
        Pre-built ``id → item`` map from the item catalog.  Build it with
        :func:`grimoire.models.roller.load_all_items`.
    table_loader:
        Loader used to look up referenced sub-tables by their ``id``.
    visited:
        Set of table IDs already seen on the current resolution path.
        Used to detect and break reference cycles.  Pass ``None`` (the
        default) to start a fresh traversal.
    parent_weight:
        Cumulative weight inherited from ancestor ``reference`` entries.
        Each entry's effective weight is ``entry_weight × parent_weight``.

    Returns
    -------
    list[dict]
        Flat list of resolved item dicts.  Each dict has a ``_weight`` key
        holding its effective weight for weighted random selection.
        Inline items (``item:`` blocks) use the name as ``_id`` when absent.
        Unresolvable ``item_ref`` entries are returned as stub dicts with
        only ``_id``, ``name``, and ``_weight``.  Unresolvable or cyclic
        ``reference`` entries are similarly stubbed as ``[Table: <id>]``.
    """
    if visited is None:
        visited = frozenset()

    resolved: list[dict] = []

    for entry in entries:
        weight = max(int(entry.get("weight", 1)), 1) * parent_weight

        if "item" in entry:
            item = dict(entry["item"])
            item.setdefault("_id", item.get("name", "inline_item"))
            item["_weight"] = weight
            resolved.append(item)

        elif "item_ref" in entry:
            item_id = str(entry["item_ref"])
            found = item_index.get(item_id)
            if found is not None:
                item = dict(found)
                item["_weight"] = weight
                resolved.append(item)
            else:
                resolved.append({"_id": item_id, "name": item_id, "_weight": weight})

        elif "reference" in entry:
            ref_id = str(entry["reference"])
            if ref_id not in visited:
                sub_table = table_loader.find_by_id(ref_id)
                if sub_table is not None:
                    resolved.extend(
                        resolve_table_entries(
                            sub_table.get("entries", []),
                            item_index,
                            table_loader,
                            visited | {ref_id},
                            weight,
                        )
                    )
                    continue
            # Sub-table not found or cycle detected — show stub.
            resolved.append(
                {
                    "_id": f"_ref:{ref_id}",
                    "name": f"[Table: {ref_id}]",
                    "_weight": weight,
                }
            )

    return resolved
