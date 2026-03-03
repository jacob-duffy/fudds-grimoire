"""Armor and shield item model."""

from typing import Optional

from grimoire.models.constants import DexBonus
from grimoire.models.data.base import BaseItem


class ArmorItem(BaseItem):
    """An armor or shield catalog entry."""

    armor_class: Optional[int] = None
    dex_bonus: DexBonus = DexBonus.NONE
    strength_req: Optional[int] = None
    stealth_disadvantage: bool = False
