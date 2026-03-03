"""Tests for grimoire.models.roller."""

import random

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.models.roller import (
    CURRENCY_DEFAULT_MAX,
    CURRENCY_DEFAULT_MIN,
    filter_items,
    load_all_items,
    roll_currency,
    roll_item,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SWORD = {
    "_id": "iron_sword",
    "name": "Iron Sword",
    "type": "weapon",
    "rarity": "common",
    "value_gp": 15,
}
SHIELD = {
    "_id": "wooden_shield",
    "name": "Wooden Shield",
    "type": "shield",
    "rarity": "common",
    "value_gp": 10,
}
POTION = {
    "_id": "healing_potion",
    "name": "Healing Potion",
    "type": "potion",
    "rarity": "common",
    "value_gp": 50,
}
RARE_RING = {
    "_id": "ring_of_power",
    "name": "Ring of Power",
    "type": "ring",
    "rarity": "rare",
    "value_gp": 500,
}
NO_VALUE = {
    "_id": "mystery_box",
    "name": "Mystery Box",
    "type": "trinket",
    "rarity": "uncommon",
}


def _seed_catalog(tmp_path, item_type: str, item_id: str, item_data: dict):
    """Write one item into a catalog file via the loader."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(item_type, item_id, item_data)


# ---------------------------------------------------------------------------
# load_all_items
# ---------------------------------------------------------------------------


def test_load_all_items_empty_catalog(tmp_path):
    """Returns an empty list when no catalog files exist."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert load_all_items(loader) == []


def test_load_all_items_single_item(tmp_path):
    """Returns one item when one is saved."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    items = load_all_items(loader)
    assert len(items) == 1
    assert items[0]["name"] == "Iron Sword"


def test_load_all_items_injects_id(tmp_path):
    """Each item dict has an _id key equal to its catalog key."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "iron_sword", SWORD)
    items = load_all_items(loader)
    assert items[0]["_id"] == "iron_sword"


def test_load_all_items_deduplicates_shared_files(tmp_path):
    """Types sharing a file (e.g. wand/staff → wondrous.yml) are not doubled."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    # Save one item under "ring" (maps to wondrous.yml).
    loader.save_item(
        "ring",
        "the_ring",
        {"name": "Dedup Ring", "type": "ring", "rarity": "rare"},
    )
    items = load_all_items(loader)
    # "wand", "staff", "rod", "ring", and "wondrous item" all share
    # wondrous.yml — the item should appear exactly once.
    ring_matches = [i for i in items if i.get("name") == "Dedup Ring"]
    assert len(ring_matches) == 1


def test_load_all_items_multiple_files(tmp_path):
    """Items from different catalog files are all returned."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    loader.save_item(
        "armor", "plate", {"name": "Plate Mail", "type": "armor", "rarity": "rare"}
    )
    items = load_all_items(loader)
    names = {i["name"] for i in items}
    assert "Iron Sword" in names
    assert "Plate Mail" in names


# ---------------------------------------------------------------------------
# filter_items
# ---------------------------------------------------------------------------


def test_filter_no_filters_returns_all():
    """With no filters, all items are returned unchanged."""
    items = [SWORD, SHIELD, POTION, RARE_RING]
    assert filter_items(items) == items


def test_filter_by_single_rarity():
    items = [SWORD, SHIELD, RARE_RING]
    result = filter_items(items, rarities=["rare"])
    assert result == [RARE_RING]


def test_filter_by_multiple_rarities():
    items = [SWORD, RARE_RING, NO_VALUE]
    result = filter_items(items, rarities=["common", "uncommon"])
    assert SWORD in result
    assert NO_VALUE in result
    assert RARE_RING not in result


def test_filter_rarity_empty_list_returns_all():
    items = [SWORD, RARE_RING]
    assert filter_items(items, rarities=[]) == items


def test_filter_type_include():
    items = [SWORD, SHIELD, POTION]
    result = filter_items(items, types=["weapon"], types_mode="include")
    assert result == [SWORD]


def test_filter_type_include_multiple():
    items = [SWORD, SHIELD, POTION]
    result = filter_items(items, types=["weapon", "shield"], types_mode="include")
    assert SWORD in result
    assert SHIELD in result
    assert POTION not in result


def test_filter_type_exclude():
    items = [SWORD, SHIELD, POTION]
    result = filter_items(items, types=["weapon"], types_mode="exclude")
    assert SWORD not in result
    assert SHIELD in result
    assert POTION in result


def test_filter_type_empty_list_returns_all():
    items = [SWORD, POTION]
    assert filter_items(items, types=[], types_mode="include") == items


def test_filter_wealth_min():
    items = [SWORD, SHIELD, POTION, RARE_RING]  # values: 15, 10, 50, 500
    result = filter_items(items, wealth_min=50)
    assert SWORD not in result
    assert SHIELD not in result
    assert POTION in result
    assert RARE_RING in result


def test_filter_wealth_max():
    items = [SWORD, SHIELD, POTION, RARE_RING]
    result = filter_items(items, wealth_max=50)
    assert SWORD in result
    assert SHIELD in result
    assert POTION in result
    assert RARE_RING not in result


def test_filter_wealth_range():
    items = [SWORD, SHIELD, POTION, RARE_RING]  # values: 15, 10, 50, 500
    result = filter_items(items, wealth_min=10, wealth_max=50)
    assert SWORD in result
    assert SHIELD in result
    assert POTION in result
    assert RARE_RING not in result


def test_filter_wealth_items_without_value_always_pass():
    """Items with no value_gp field are never filtered out by wealth range."""
    result = filter_items([NO_VALUE], wealth_min=1000, wealth_max=9999)
    assert result == [NO_VALUE]


def test_filter_combined():
    items = [SWORD, SHIELD, POTION, RARE_RING, NO_VALUE]
    result = filter_items(
        items,
        rarities=["common"],
        types=["weapon", "potion"],
        types_mode="include",
        wealth_min=10,
        wealth_max=100,
    )
    assert SWORD in result
    assert POTION in result
    assert SHIELD not in result  # filtered by type
    assert RARE_RING not in result  # filtered by rarity and value


# ---------------------------------------------------------------------------
# filter_items — rarity comparator modes
# ---------------------------------------------------------------------------

# Build a diverse item list covering every ranked rarity.
_ITEMS_BY_RARITY = [
    {"name": "c", "rarity": "common", "type": "trinket"},
    {"name": "u", "rarity": "uncommon", "type": "trinket"},
    {"name": "r", "rarity": "rare", "type": "trinket"},
    {"name": "vr", "rarity": "very rare", "type": "trinket"},
    {"name": "l", "rarity": "legendary", "type": "trinket"},
    {"name": "a", "rarity": "artifact", "type": "trinket"},
    {"name": "v", "rarity": "varies", "type": "trinket"},
]


def _names(items):
    return {i["name"] for i in items}


def test_filter_rarity_eq():
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="eq", rarity_ref="rare")
    assert _names(result) == {"r"}


def test_filter_rarity_geq():
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="geq", rarity_ref="rare")
    assert _names(result) == {"r", "vr", "l", "a"}


def test_filter_rarity_gt():
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="gt", rarity_ref="rare")
    assert _names(result) == {"vr", "l", "a"}


def test_filter_rarity_leq():
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="leq", rarity_ref="uncommon")
    assert _names(result) == {"c", "u"}


def test_filter_rarity_lt():
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="lt", rarity_ref="uncommon")
    assert _names(result) == {"c"}


def test_filter_rarity_comparator_excludes_varies():
    """Items with 'varies' rarity have no rank and are excluded by comparators."""
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="geq", rarity_ref="common")
    assert "v" not in _names(result)


def test_filter_rarity_comparator_unknown_ref_returns_empty():
    """An unknown rarity_ref value (not in RARITY_RANK) returns no results."""
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="geq", rarity_ref="varies")
    assert result == []


def test_filter_rarity_manual_with_no_selection_returns_all():
    """Manual mode with empty rarities list returns all items unchanged."""
    result = filter_items(_ITEMS_BY_RARITY, rarity_mode="manual", rarities=[])
    assert result == _ITEMS_BY_RARITY


# ---------------------------------------------------------------------------
# roll_currency
# ---------------------------------------------------------------------------


def test_roll_currency_within_range():
    rng = random.Random(0)
    for _ in range(50):
        result = roll_currency(10.0, 100.0, rng)
        assert 10.0 <= result["value_gp"] <= 100.0


def test_roll_currency_equal_min_max():
    result = roll_currency(42.0, 42.0)
    assert result["value_gp"] == 42.0
    assert result["name"] == "42 gp"


def test_roll_currency_returns_int_name_for_whole():
    result = roll_currency(5.0, 5.0)
    assert result["name"] == "5 gp"


def test_roll_currency_result_shape():
    result = roll_currency(1.0, 10.0)
    assert result["type"] == "currency"
    assert result["rarity"] == "common"
    assert "_id" in result
    assert "name" in result
    assert "value_gp" in result


# ---------------------------------------------------------------------------
# roll_item
# ---------------------------------------------------------------------------


def test_roll_item_empty_catalog_returns_none(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert roll_item(loader) is None


def test_roll_item_returns_item_from_catalog(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    result = roll_item(loader, rng=random.Random(1))
    assert result is not None
    assert result["name"] == "Iron Sword"


def test_roll_item_rarity_filter_no_match(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)  # rarity: common
    result = roll_item(loader, rarities=["legendary"])
    assert result is None


def test_roll_item_rarity_filter_match(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)  # rarity: common
    loader.save_item("ring", "ring", {"name": "Ring", "type": "ring", "rarity": "rare"})
    result = roll_item(loader, rarities=["rare"], rng=random.Random(0))
    assert result is not None
    assert result["rarity"] == "rare"


def test_roll_item_type_include_filter(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    loader.save_item(
        "potion", "hp", {"name": "HP", "type": "potion", "rarity": "common"}
    )
    result = roll_item(
        loader,
        types=["weapon"],
        types_mode="include",
        rng=random.Random(0),
    )
    assert result is not None
    assert result["type"] == "weapon"


def test_roll_item_type_exclude_filter(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    loader.save_item(
        "potion", "hp", {"name": "HP", "type": "potion", "rarity": "common"}
    )
    result = roll_item(
        loader,
        types=["weapon"],
        types_mode="exclude",
        rng=random.Random(0),
    )
    assert result is not None
    assert result["type"] == "potion"


def test_roll_item_currency_shortcut(tmp_path):
    """Currency-only include fires shortcut and value is within range."""
    loader = ItemCatalogLoader(data_dir=tmp_path)  # empty catalog
    result = roll_item(
        loader,
        types=["currency"],
        types_mode="include",
        wealth_min=10.0,
        wealth_max=100.0,
        rng=random.Random(0),
    )
    assert result is not None
    assert result["type"] == "currency"
    assert 10.0 <= result["value_gp"] <= 100.0


def test_roll_item_currency_shortcut_no_range_uses_defaults(tmp_path):
    """Currency shortcut uses 0–500 defaults when no wealth range is given."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    result = roll_item(
        loader,
        types=["currency"],
        types_mode="include",
        rng=random.Random(0),
    )
    assert result is not None
    assert result["type"] == "currency"
    assert CURRENCY_DEFAULT_MIN <= result["value_gp"] <= CURRENCY_DEFAULT_MAX


def test_roll_item_currency_shortcut_partial_range_uses_defaults(tmp_path):
    """Currency shortcut applies when only one bound is set; other defaults."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    # Only min provided — max should default to 500.
    result = roll_item(
        loader,
        types=["currency"],
        types_mode="include",
        wealth_min=200.0,
        rng=random.Random(0),
    )
    assert result is not None
    assert 200.0 <= result["value_gp"] <= CURRENCY_DEFAULT_MAX


def test_roll_item_currency_shortcut_not_triggered_with_other_types(tmp_path):
    """Shortcut does not fire when more than one type is in the include list."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)
    result = roll_item(
        loader,
        types=["currency", "weapon"],
        types_mode="include",
        wealth_min=1.0,
        wealth_max=50.0,
        rng=random.Random(0),
    )
    # Should reach catalog path and return the sword (value_gp=15, in range).
    assert result is not None
    assert result["name"] == "Iron Sword"


def test_roll_item_wealth_range_filter(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "sword", SWORD)  # value_gp=15
    loader.save_item(
        "ring",
        "ring_of_power",
        {"name": "Ring of Power", "type": "ring", "rarity": "rare", "value_gp": 500},
    )
    result = roll_item(loader, wealth_max=50, rng=random.Random(0))
    assert result is not None
    assert result["value_gp"] <= 50


def test_roll_item_seeded_rng_is_deterministic(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    for i in range(5):
        loader.save_item(
            "trinket",
            f"item{i}",
            {"name": f"Item {i}", "type": "trinket", "rarity": "common"},
        )
    r1 = roll_item(loader, rng=random.Random(42))
    r2 = roll_item(loader, rng=random.Random(42))
    assert r1 is not None
    assert r1["_id"] == r2["_id"]
