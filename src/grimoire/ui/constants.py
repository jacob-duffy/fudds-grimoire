"""UI-layer constants for Fudd's Grimoire.

Flat string lists derived from domain enums plus display-only mappings used
across multiple screens.  Centralised here so screens stay free of duplication.
"""

from grimoire.models.constants import (
    Activation,
    DamageType,
    Denomination,
    DexBonus,
    ItemType,
    Rarity,
    WeaponProperty,
)

# Flat string lists for Select / SelectionList widgets
ACTIVATION_OPTIONS: list[str] = list(Activation)
DAMAGE_TYPES: list[str] = list(DamageType)
DENOMINATION_OPTIONS: list[str] = list(Denomination)
DEX_BONUS_OPTIONS: list[str] = list(DexBonus)
ITEM_TYPES: list[str] = list(ItemType)
RARITIES: list[str] = list(Rarity)
WEAPON_PROPERTIES: list[str] = list(WeaponProperty)

# Human-readable labels for rarity values shown in filter controls
RARITY_LABELS: dict[str, str] = {
    "common": "Common",
    "uncommon": "Uncommon",
    "rare": "Rare",
    "very rare": "Very Rare",
    "legendary": "Legendary",
    "artifact": "Artifact",
    "varies": "Varies",
}

# Options for the rarity comparison-mode Select widget on the Roll Item screen
RARITY_MODE_OPTIONS: list[tuple[str, str]] = [
    ("Manual", "manual"),
    ("= (exactly)", "eq"),
    ("\u2265 (at least)", "geq"),
    ("> (above)", "gt"),
    ("\u2264 (at most)", "leq"),
    ("< (below)", "lt"),
]

# Magic bonus Select options shared by weapon and armor sub-forms
MAGIC_BONUS_OPTIONS: list[tuple[str, str]] = [
    ("None", ""),
    ("+1", "1"),
    ("+2", "2"),
    ("+3", "3"),
]

# Include / exclude toggle options for the type filter on the Roll Item screen
TYPE_MODE_OPTIONS: list[tuple[str, str]] = [
    ("Include", "include"),
    ("Exclude", "exclude"),
]
