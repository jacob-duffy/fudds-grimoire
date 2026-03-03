"""Backward-compatibility shim — import from canonical modules instead.

Preferred import paths:
  constants  → ``grimoire.models.constants``
  slugify    → ``grimoire.utils``
  TYPE_TO_FILE / TYPE_TO_SUBFORM → ``grimoire.loaders.items``
"""

from grimoire.models.constants import RARITY_RANK  # noqa: F401 — re-exported for compat
from grimoire.models.constants import (
    SUBFORM_IDS,
    Activation,
    DamageType,
    Denomination,
    DexBonus,
    ItemType,
    Rarity,
    WeaponProperty,
)
from grimoire.utils import slugify  # noqa: F401

# Flat list aliases — StrEnum members are strings, so these behave identically
# to the old plain lists for all existing callers.
ITEM_TYPES: list[str] = list(ItemType)
RARITIES: list[str] = list(Rarity)
DAMAGE_TYPES: list[str] = list(DamageType)
WEAPON_PROPERTIES: list[str] = list(WeaponProperty)
DEX_BONUS_OPTIONS: list[str] = list(DexBonus)
ACTIVATION_OPTIONS: list[str] = list(Activation)
DENOMINATION_OPTIONS: list[str] = list(Denomination)

__all__ = [
    "ACTIVATION_OPTIONS",
    "DAMAGE_TYPES",
    "DENOMINATION_OPTIONS",
    "DEX_BONUS_OPTIONS",
    "ITEM_TYPES",
    "RARITIES",
    "RARITY_RANK",
    "SUBFORM_IDS",
    "WEAPON_PROPERTIES",
    "slugify",
    # Enums
    "Activation",
    "DamageType",
    "DexBonus",
    "Denomination",
    "ItemType",
    "Rarity",
    "WeaponProperty",
]
