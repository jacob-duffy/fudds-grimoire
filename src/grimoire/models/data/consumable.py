"""Consumable item model (potions, scrolls, generic consumables)."""

from typing import Optional

from grimoire.models.constants import Activation
from grimoire.models.data.base import BaseItem


class ConsumableItem(BaseItem):
    """A consumable catalog entry — potions, scrolls, one-use items."""

    charges: Optional[int] = None
    activation: Optional[Activation] = None
    effect: Optional[str] = None
