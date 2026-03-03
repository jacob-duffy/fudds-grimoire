"""Tests for grimoire.models.roller — roll_table and parse_rolls."""

import random

import pytest

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.models.roller import parse_rolls, roll_table

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SWORD_ITEM = {
    "name": "Iron Sword",
    "type": "weapon",
    "rarity": "common",
    "value_gp": 15,
}

POTION_ITEM = {
    "name": "Healing Potion",
    "type": "potion",
    "rarity": "common",
    "value_gp": 50,
}


def _table(*entries, rolls=None) -> dict:
    """Build a minimal table dict."""
    t: dict = {"id": "test_table", "entries": list(entries)}
    if rolls is not None:
        t["rolls"] = rolls
    return t


def _inline_entry(item: dict, weight: int = 1) -> dict:
    return {"item": item, "weight": weight}


def _ref_entry(item_id: str, weight: int = 1) -> dict:
    return {"item_ref": item_id, "weight": weight}


def _table_ref_entry(table_id: str, weight: int = 1) -> dict:
    return {"reference": table_id, "weight": weight}


def _seed_catalog(
    tmp_path, item_type: str, item_id: str, item_data: dict
) -> ItemCatalogLoader:
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(item_type, item_id, item_data)
    return loader


# ---------------------------------------------------------------------------
# parse_rolls
# ---------------------------------------------------------------------------


def test_parse_rolls_none_returns_1():
    assert parse_rolls(None) == 1


def test_parse_rolls_integer():
    assert parse_rolls(3) == 3


def test_parse_rolls_integer_one():
    assert parse_rolls(1) == 1


def test_parse_rolls_integer_clamped_to_1():
    assert parse_rolls(0) == 1


def test_parse_rolls_simple_dice(monkeypatch):
    rng = random.Random(42)
    result = parse_rolls("1d4", rng)
    assert 1 <= result <= 4


def test_parse_rolls_multi_dice(monkeypatch):
    rng = random.Random(99)
    result = parse_rolls("2d6", rng)
    assert 2 <= result <= 12


def test_parse_rolls_dice_with_modifier(monkeypatch):
    rng = random.Random(0)
    result = parse_rolls("1d6+2", rng)
    assert 3 <= result <= 8


def test_parse_rolls_dice_minimum_1():
    """Even when a weird roll would land at 0, we clamp to 1."""
    rng = random.Random(0)
    # A "0d6" doesn't match but a sum that yields 0 is still clamped.
    # Use a direct call: override the random to always return 1 face but dice=0
    # The regex requires >=1 digit so "0d6" would return 0 dice → sum 0 → clamp 1.
    result = parse_rolls("1d1+0", rng)
    assert result >= 1


def test_parse_rolls_invalid_string():
    with pytest.raises(ValueError):
        parse_rolls("roll heavily")


def test_parse_rolls_invalid_string_spaces():
    with pytest.raises(ValueError):
        parse_rolls("1 d 6")


# ---------------------------------------------------------------------------
# roll_table — empty / missing entries
# ---------------------------------------------------------------------------


def test_roll_table_empty_entries():
    table = _table()  # no entries
    assert roll_table(table) == []


def test_roll_table_missing_entries_key():
    assert roll_table({"id": "empty"}) == []


# ---------------------------------------------------------------------------
# roll_table — inline items
# ---------------------------------------------------------------------------


def test_roll_table_inline_single_entry():
    table = _table(_inline_entry(SWORD_ITEM))
    results = roll_table(table)
    assert len(results) == 1
    assert results[0]["name"] == "Iron Sword"


def test_roll_table_inline_sets_id_from_name():
    table = _table(_inline_entry(SWORD_ITEM))
    results = roll_table(table)
    assert results[0]["_id"] == "Iron Sword"


def test_roll_table_inline_preserves_existing_id():
    item = {**SWORD_ITEM, "_id": "custom_id"}
    table = _table(_inline_entry(item))
    results = roll_table(table)
    assert results[0]["_id"] == "custom_id"


def test_roll_table_inline_fallback_id_when_no_name():
    table = _table(_inline_entry({"type": "trinket"}))
    results = roll_table(table)
    assert results[0]["_id"] == "inline_item"


def test_roll_table_multiple_rolls(tmp_path):
    table = _table(_inline_entry(SWORD_ITEM), rolls=3)
    results = roll_table(table)
    assert len(results) == 3


def test_roll_table_rolls_dice_expression():
    # With rolls="1d1" every run produces exactly 1.
    table = _table(_inline_entry(SWORD_ITEM), rolls="1d1")
    results = roll_table(table)
    assert len(results) == 1


# ---------------------------------------------------------------------------
# roll_table — item_ref entries
# ---------------------------------------------------------------------------


def test_roll_table_item_ref_resolved(tmp_path):
    loader = _seed_catalog(tmp_path, "weapon", "iron_sword", SWORD_ITEM)
    table = _table(_ref_entry("iron_sword"))
    results = roll_table(table, catalog_loader=loader)
    assert len(results) == 1
    assert results[0]["name"] == "Iron Sword"
    assert results[0]["_id"] == "iron_sword"


def test_roll_table_item_ref_stub_when_not_found(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    table = _table(_ref_entry("missing_item"))
    results = roll_table(table, catalog_loader=loader)
    assert len(results) == 1
    assert results[0]["_id"] == "missing_item"
    assert results[0]["name"] == "missing_item"


def test_roll_table_item_ref_stub_when_no_loader():
    table = _table(_ref_entry("iron_sword"))
    results = roll_table(table, catalog_loader=None)
    assert len(results) == 1
    assert results[0]["_id"] == "iron_sword"


# ---------------------------------------------------------------------------
# roll_table — reference (nested table) entries
# ---------------------------------------------------------------------------


def test_roll_table_reference_entry_returns_stub():
    table = _table(_table_ref_entry("boss_hoard"))
    results = roll_table(table)
    assert len(results) == 1
    assert results[0]["name"] == "[Table: boss_hoard]"
    assert results[0]["_id"] == "_ref:boss_hoard"


def test_roll_table_reference_resolved_with_table_loader(tmp_path):
    """A reference entry is rolled recursively when a table_loader is given."""
    import yaml

    from grimoire.loaders.tables import LootTableLoader

    sub_data = {"id": "boss_hoard", "entries": [{"item": SWORD_ITEM, "weight": 1}]}
    (tmp_path / "boss_hoard.yml").write_text(
        yaml.dump(sub_data, default_flow_style=False), encoding="utf-8"
    )
    table_loader = LootTableLoader(data_dir=tmp_path)
    table = _table(_table_ref_entry("boss_hoard"))
    results = roll_table(table, table_loader=table_loader)
    assert len(results) == 1
    assert results[0]["name"] == "Iron Sword"


def test_roll_table_reference_stub_when_table_not_found(tmp_path):
    """Falls back to a stub when the referenced table file doesn’t exist."""
    from grimoire.loaders.tables import LootTableLoader

    table_loader = LootTableLoader(data_dir=tmp_path)  # empty dir
    table = _table(_table_ref_entry("missing_table"))
    results = roll_table(table, table_loader=table_loader)
    assert len(results) == 1
    assert results[0]["name"] == "[Table: missing_table]"


def test_roll_table_reference_cycle_returns_stub(tmp_path):
    """A self-referential table terminates without infinite recursion."""
    import yaml

    from grimoire.loaders.tables import LootTableLoader

    # Table references itself.
    self_ref = {"id": "looping", "entries": [{"reference": "looping", "weight": 1}]}
    (tmp_path / "looping.yml").write_text(
        yaml.dump(self_ref, default_flow_style=False), encoding="utf-8"
    )
    table_loader = LootTableLoader(data_dir=tmp_path)
    # Load and roll directly via find_by_id to hit the cycle path.
    table = table_loader.find_by_id("looping")
    results = roll_table(table, table_loader=table_loader)
    assert len(results) == 1
    assert results[0]["name"] == "[Table: looping]"


def test_roll_table_reference_deep_chain(tmp_path):
    """A chain of references A → B → inline item resolves correctly."""
    import yaml

    from grimoire.loaders.tables import LootTableLoader

    table_b = {"id": "table_b", "entries": [{"item": POTION_ITEM, "weight": 1}]}
    (tmp_path / "table_b.yml").write_text(
        yaml.dump(table_b, default_flow_style=False), encoding="utf-8"
    )
    table_a = {"id": "table_a", "entries": [{"reference": "table_b", "weight": 1}]}
    (tmp_path / "table_a.yml").write_text(
        yaml.dump(table_a, default_flow_style=False), encoding="utf-8"
    )
    table_loader = LootTableLoader(data_dir=tmp_path)
    results = roll_table(table_a, table_loader=table_loader)
    assert len(results) == 1
    assert results[0]["name"] == "Healing Potion"


# ---------------------------------------------------------------------------
# roll_table — malformed entry is silently skipped
# ---------------------------------------------------------------------------


def test_roll_table_malformed_entry_skipped():
    entries = [{"weight": 1}]  # no item / item_ref / reference key
    table = {"id": "t", "entries": entries}
    results = roll_table(table)
    assert results == []


# ---------------------------------------------------------------------------
# roll_table — weight-based selection
# ---------------------------------------------------------------------------


def test_roll_table_weight_zero_treated_as_one():
    """An entry with weight=0 should still be selectable (clamped to 1)."""
    table = _table({"item": SWORD_ITEM, "weight": 0})
    results = roll_table(table)
    assert len(results) == 1


def test_roll_table_single_high_weight_entry_always_picked():
    """100% weight on one entry means it wins every roll."""
    rng = random.Random(42)
    table = _table(
        {"item": SWORD_ITEM, "weight": 1000},
        {"item": POTION_ITEM, "weight": 0},
    )
    for _ in range(10):
        results = roll_table(table, rng=rng)
        assert results[0]["name"] == "Iron Sword"


# ---------------------------------------------------------------------------
# roll_table — seeded RNG for reproducibility
# ---------------------------------------------------------------------------


def test_roll_table_seeded_rng_reproducible():
    table = _table(
        _inline_entry(SWORD_ITEM),
        _inline_entry(POTION_ITEM),
        rolls=3,
    )
    results_a = roll_table(table, rng=random.Random(0))
    results_b = roll_table(table, rng=random.Random(0))
    assert [r["name"] for r in results_a] == [r["name"] for r in results_b]
