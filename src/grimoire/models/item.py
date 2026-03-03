"""Item type constants, schema mappings, and utility helpers."""

import re

ITEM_TYPES: list[str] = [
    "weapon",
    "armor",
    "shield",
    "consumable",
    "potion",
    "scroll",
    "wand",
    "staff",
    "rod",
    "ring",
    "wondrous item",
    "tool",
    "ammunition",
    "trinket",
    "currency",
    "gem",
    "art object",
    "trade good",
    "vehicle",
    "other",
]

RARITIES: list[str] = [
    "common",
    "uncommon",
    "rare",
    "very rare",
    "legendary",
    "artifact",
    "varies",
]

DAMAGE_TYPES: list[str] = [
    "slashing",
    "piercing",
    "bludgeoning",
    "fire",
    "cold",
    "lightning",
    "thunder",
    "acid",
    "poison",
    "necrotic",
    "radiant",
    "psychic",
    "force",
]

WEAPON_PROPERTIES: list[str] = [
    "ammunition",
    "finesse",
    "heavy",
    "light",
    "loading",
    "range",
    "reach",
    "special",
    "thrown",
    "two-handed",
    "versatile",
    "silvered",
    "adamantine",
]

DEX_BONUS_OPTIONS: list[str] = ["none", "max+2", "full"]

ACTIVATION_OPTIONS: list[str] = [
    "action",
    "bonus action",
    "reaction",
    "no action",
    "1 minute",
    "10 minutes",
    "1 hour",
]

DENOMINATION_OPTIONS: list[str] = ["cp", "sp", "ep", "gp", "pp"]

# Maps item type → catalog filename under .data/items/
TYPE_TO_FILE: dict[str, str] = {
    "weapon": "weapons.yml",
    "armor": "armor.yml",
    "shield": "armor.yml",
    "consumable": "consumables.yml",
    "potion": "consumables.yml",
    "scroll": "consumables.yml",
    "wand": "wondrous.yml",
    "staff": "wondrous.yml",
    "rod": "wondrous.yml",
    "ring": "wondrous.yml",
    "wondrous item": "wondrous.yml",
    "tool": "tools.yml",
    "ammunition": "ammunition.yml",
    "trinket": "trinkets.yml",
    "currency": "currency.yml",
    "gem": "valuables.yml",
    "art object": "valuables.yml",
    "trade good": "valuables.yml",
    "vehicle": "vehicles.yml",
    "other": "items.yml",
}

# Maps item type → which sub-form group to display (None = no sub-form)
TYPE_TO_SUBFORM: dict[str, str | None] = {
    "weapon": "weapon",
    "armor": "armor",
    "shield": "armor",
    "consumable": "consumable",
    "potion": "consumable",
    "scroll": "consumable",
    "wand": "wondrous",
    "staff": "wondrous",
    "rod": "wondrous",
    "ring": "wondrous",
    "wondrous item": "wondrous",
    "currency": "currency",
}

# All sub-form IDs used in the UI
SUBFORM_IDS: list[str] = ["weapon", "armor", "consumable", "wondrous", "currency"]


def slugify(name: str) -> str:
    """Convert a display name to a snake_case item ID.

    Examples:
        >>> slugify("Iron Sword")
        'iron_sword'
        >>> slugify("+1 Longsword")
        '1_longsword'
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")
