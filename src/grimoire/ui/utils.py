"""UI-layer utility helpers for Fudd's Grimoire.

Reusable helpers for building Textual Select / SelectionList option lists.
"""

from textual.widgets.selection_list import Selection

from grimoire.models.constants import RARITY_RANK
from grimoire.ui.constants import ITEM_TYPES, RARITIES, RARITY_LABELS


def opts(values: list[str]) -> list[tuple[str, str]]:
    """Convert a list of strings to ``(label, value)`` Select option tuples."""
    return [(v, v) for v in values]


def rarity_selections() -> list[Selection]:
    """Return ``Selection`` objects for every rarity value, in enum order."""
    return [Selection(RARITY_LABELS.get(r, r.title()), r) for r in RARITIES]


def rarity_comparator_options() -> list[tuple[str, str]]:
    """Return ``(label, value)`` tuples for the rarity comparator Select.

    Only rarities present in ``RARITY_RANK`` (i.e. those on a linear scale)
    are included; ``"varies"`` is intentionally omitted.
    """
    return [(RARITY_LABELS.get(r, r.title()), r) for r in RARITY_RANK]


def type_selections() -> list[Selection]:
    """Return ``Selection`` objects for every item type, in enum order."""
    return [Selection(t.title(), t) for t in ITEM_TYPES]
