"""Canonical enum constants and lookup tables for item domain values."""

from enum import StrEnum


class ItemType(StrEnum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    CONSUMABLE = "consumable"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    STAFF = "staff"
    ROD = "rod"
    RING = "ring"
    WONDROUS_ITEM = "wondrous item"
    TOOL = "tool"
    AMMUNITION = "ammunition"
    TRINKET = "trinket"
    CURRENCY = "currency"
    GEM = "gem"
    ART_OBJECT = "art object"
    TRADE_GOOD = "trade good"
    VEHICLE = "vehicle"
    OTHER = "other"


class Rarity(StrEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    VARIES = "varies"


class DamageType(StrEnum):
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    THUNDER = "thunder"
    ACID = "acid"
    POISON = "poison"
    NECROTIC = "necrotic"
    RADIANT = "radiant"
    PSYCHIC = "psychic"
    FORCE = "force"


class WeaponProperty(StrEnum):
    AMMUNITION = "ammunition"
    FINESSE = "finesse"
    HEAVY = "heavy"
    LIGHT = "light"
    LOADING = "loading"
    RANGE = "range"
    REACH = "reach"
    SPECIAL = "special"
    THROWN = "thrown"
    TWO_HANDED = "two-handed"
    VERSATILE = "versatile"
    SILVERED = "silvered"
    ADAMANTINE = "adamantine"


class DexBonus(StrEnum):
    NONE = "none"
    MAX_PLUS_2 = "max+2"
    FULL = "full"


class Activation(StrEnum):
    ACTION = "action"
    BONUS_ACTION = "bonus action"
    REACTION = "reaction"
    NO_ACTION = "no action"
    ONE_MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    ONE_HOUR = "1 hour"


class Denomination(StrEnum):
    CP = "cp"
    SP = "sp"
    EP = "ep"
    GP = "gp"
    PP = "pp"


# Ordinal rank for rarities that sit on a linear scale.
# "varies" is intentionally absent — it has no meaningful position.
RARITY_RANK: dict[str, int] = {
    Rarity.COMMON: 0,
    Rarity.UNCOMMON: 1,
    Rarity.RARE: 2,
    Rarity.VERY_RARE: 3,
    Rarity.LEGENDARY: 4,
    Rarity.ARTIFACT: 5,
}

# All sub-form IDs used in the UI
SUBFORM_IDS: list[str] = ["weapon", "armor", "consumable", "wondrous", "currency"]
