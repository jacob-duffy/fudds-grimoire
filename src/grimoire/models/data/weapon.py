"""Weapon item model."""

from typing import Optional

from pydantic import Field

from grimoire.models.constants import DamageType, WeaponProperty
from grimoire.models.data.base import BaseItem


class WeaponItem(BaseItem):
    """A weapon catalog entry with combat statistics."""

    damage_dice: Optional[str] = None
    damage_type: Optional[DamageType] = None
    properties: list[WeaponProperty] = Field(default_factory=list)
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
