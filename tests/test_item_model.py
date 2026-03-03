"""Tests for grimoire.models.item constants and helpers."""

from grimoire.models.item import (
    ACTIVATION_OPTIONS,
    DAMAGE_TYPES,
    DENOMINATION_OPTIONS,
    DEX_BONUS_OPTIONS,
    ITEM_TYPES,
    RARITIES,
    SUBFORM_IDS,
    TYPE_TO_FILE,
    TYPE_TO_SUBFORM,
    WEAPON_PROPERTIES,
    slugify,
)

# -- slugify ------------------------------------------------------------------


def test_slugify_simple():
    assert slugify("Iron Sword") == "iron_sword"


def test_slugify_plus_prefix():
    assert slugify("+1 Longsword") == "1_longsword"


def test_slugify_special_chars():
    assert slugify("Ace of Spades!") == "ace_of_spades"


def test_slugify_leading_trailing_spaces():
    assert slugify("  Ring  ") == "ring"


def test_slugify_multiple_separators():
    assert slugify("Wand  --  of  Fire") == "wand_of_fire"


# -- constants ----------------------------------------------------------------


def test_all_item_types_have_file_mapping():
    """Every item type must map to a catalog filename."""
    for item_type in ITEM_TYPES:
        assert (
            item_type in TYPE_TO_FILE
        ), f"Missing TYPE_TO_FILE entry for '{item_type}'"


def test_type_to_file_values_end_with_yml():
    for filename in TYPE_TO_FILE.values():
        assert filename.endswith(".yml"), f"Expected .yml, got '{filename}'"


def test_subform_ids_are_subset_of_valid_names():
    valid = {"weapon", "armor", "consumable", "wondrous", "currency"}
    assert set(SUBFORM_IDS) == valid


def test_type_to_subform_values_are_valid_or_absent():
    for item_type, subform in TYPE_TO_SUBFORM.items():
        if subform is not None:
            assert (
                subform in SUBFORM_IDS
            ), f"'{item_type}' maps to unknown subform '{subform}'"


def test_item_types_not_empty():
    assert len(ITEM_TYPES) > 0


def test_rarities_include_standard_tiers():
    for rarity in ("common", "uncommon", "rare", "very rare", "legendary"):
        assert rarity in RARITIES


def test_damage_types_complete():
    for dt in ("slashing", "piercing", "bludgeoning", "fire", "cold"):
        assert dt in DAMAGE_TYPES


def test_weapon_properties_complete():
    assert "finesse" in WEAPON_PROPERTIES
    assert "two-handed" in WEAPON_PROPERTIES


def test_dex_bonus_options():
    assert DEX_BONUS_OPTIONS == ["none", "max+2", "full"]


def test_activation_options_not_empty():
    assert len(ACTIVATION_OPTIONS) > 0


def test_denomination_options():
    assert set(DENOMINATION_OPTIONS) == {"cp", "sp", "ep", "gp", "pp"}
