"""Wondrous item model (wands, staves, rods, rings, wondrous items)."""

from typing import Optional

from grimoire.models.constants import Activation
from grimoire.models.data.base import BaseItem


class WondrousItem(BaseItem):
    """A wondrous item catalog entry — wands, staves, rings, etc."""

    charges: Optional[int] = None
    max_charges: Optional[int] = None
    activation: Optional[Activation] = None
    effect: Optional[str] = None
