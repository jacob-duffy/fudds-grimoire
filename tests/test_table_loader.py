"""Tests for grimoire.loaders.tables.LootTableLoader."""

from pathlib import Path

import yaml

from grimoire.loaders.tables import _TABLE_SCHEMA_COMMENT, LootTableLoader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_table(path: Path, table_id: str, entries: list | None = None) -> None:
    """Write a minimal valid loot table YAML file."""
    data = {
        "id": table_id,
        "entries": entries or [{"item_ref": "iron_sword", "weight": 1}],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_TABLE_SCHEMA_COMMENT)
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# list_tables
# ---------------------------------------------------------------------------


def test_list_tables_empty_when_dir_missing(tmp_path):
    loader = LootTableLoader(data_dir=tmp_path / "nonexistent")
    assert loader.list_tables() == []


def test_list_tables_empty_when_dir_has_no_yml(tmp_path):
    (tmp_path / "readme.txt").write_text("nothing here")
    loader = LootTableLoader(data_dir=tmp_path)
    assert loader.list_tables() == []


def test_list_tables_returns_label_and_path(tmp_path):
    _write_table(tmp_path / "dungeon.yml", "dungeon_chest")
    loader = LootTableLoader(data_dir=tmp_path)
    results = loader.list_tables()
    assert len(results) == 1
    label, path = results[0]
    assert label == "dungeon_chest"
    assert path == tmp_path / "dungeon.yml"


def test_list_tables_falls_back_to_stem_when_no_id(tmp_path):
    (tmp_path / "mystery.yml").write_text("entries: []\n")
    loader = LootTableLoader(data_dir=tmp_path)
    label, _ = loader.list_tables()[0]
    assert label == "mystery"


def test_list_tables_sorted_alphabetically(tmp_path):
    _write_table(tmp_path / "z_table.yml", "zebra_loot")
    _write_table(tmp_path / "a_table.yml", "alpha_loot")
    loader = LootTableLoader(data_dir=tmp_path)
    labels = [label for label, _ in loader.list_tables()]
    assert labels == ["alpha_loot", "zebra_loot"]


def test_list_tables_multiple_files(tmp_path):
    for name in ("shop.yml", "dungeon.yml", "boss.yml"):
        _write_table(tmp_path / name, name.replace(".yml", ""))
    loader = LootTableLoader(data_dir=tmp_path)
    assert len(loader.list_tables()) == 3


def test_list_tables_skips_unreadable_gracefully(tmp_path):
    """A YAML parse error in one file should not raise; label falls back to stem."""
    (tmp_path / "broken.yml").write_text(": invalid: yaml: {{")
    loader = LootTableLoader(data_dir=tmp_path)
    results = loader.list_tables()
    assert len(results) == 1
    assert results[0][0] == "broken"


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------


def test_load_nonexistent_returns_skeleton(tmp_path):
    loader = LootTableLoader(data_dir=tmp_path)
    result = loader.load(tmp_path / "ghost.yml")
    assert result == {"id": "", "entries": []}


def test_load_valid_table(tmp_path):
    path = tmp_path / "cave.yml"
    _write_table(path, "cave_loot")
    loader = LootTableLoader(data_dir=tmp_path)
    data = loader.load(path)
    assert data["id"] == "cave_loot"
    assert isinstance(data["entries"], list)


def test_load_table_without_entries_gets_empty_list(tmp_path):
    path = tmp_path / "bare.yml"
    path.write_text("id: bare\n")
    loader = LootTableLoader(data_dir=tmp_path)
    data = loader.load(path)
    assert data["entries"] == []


def test_load_invalid_yaml_returns_skeleton(tmp_path):
    path = tmp_path / "bad.yml"
    path.write_text(": broken: {{")
    loader = LootTableLoader(data_dir=tmp_path)
    result = loader.load(path)
    assert result == {"id": "", "entries": []}


# ---------------------------------------------------------------------------
# append_inline_item
# ---------------------------------------------------------------------------


def test_append_inline_item_adds_entry(tmp_path):
    path = tmp_path / "loot.yml"
    _write_table(path, "test_table")
    loader = LootTableLoader(data_dir=tmp_path)
    item = {"name": "Flame Tongue", "type": "weapon", "rarity": "rare"}
    loader.append_inline_item(path, item)

    data = loader.load(path)
    inline_entries = [e for e in data["entries"] if "item" in e]
    assert len(inline_entries) == 1
    assert inline_entries[0]["item"]["name"] == "Flame Tongue"
    assert inline_entries[0]["weight"] == 1


def test_append_inline_item_custom_weight(tmp_path):
    path = tmp_path / "loot.yml"
    _write_table(path, "weighted_table")
    loader = LootTableLoader(data_dir=tmp_path)
    loader.append_inline_item(
        path, {"name": "Gold Coin", "type": "currency", "rarity": "common"}, weight=5
    )
    data = loader.load(path)
    inline = next(e for e in data["entries"] if "item" in e)
    assert inline["weight"] == 5


def test_append_multiple_inline_items(tmp_path):
    path = tmp_path / "loot.yml"
    _write_table(path, "multi_table")
    loader = LootTableLoader(data_dir=tmp_path)
    loader.append_inline_item(
        path, {"name": "A", "type": "trinket", "rarity": "common"}
    )
    loader.append_inline_item(
        path, {"name": "B", "type": "trinket", "rarity": "common"}
    )

    data = loader.load(path)
    inline = [e for e in data["entries"] if "item" in e]
    assert len(inline) == 2
    assert {e["item"]["name"] for e in inline} == {"A", "B"}


def test_append_inline_item_creates_parent_dirs(tmp_path):
    path = tmp_path / "deep" / "nested" / "table.yml"
    loader = LootTableLoader(data_dir=tmp_path)
    loader.append_inline_item(
        path, {"name": "Pebble", "type": "trinket", "rarity": "common"}
    )
    assert path.exists()


def test_append_inline_item_writes_schema_comment(tmp_path):
    path = tmp_path / "loot.yml"
    _write_table(path, "schema_test")
    loader = LootTableLoader(data_dir=tmp_path)
    loader.append_inline_item(
        path, {"name": "X", "type": "trinket", "rarity": "common"}
    )
    assert _TABLE_SCHEMA_COMMENT.strip() in path.read_text()


def test_append_to_nonexistent_file_creates_it(tmp_path):
    path = tmp_path / "brand_new.yml"
    loader = LootTableLoader(data_dir=tmp_path)
    loader.append_inline_item(
        path, {"name": "Ghost Candle", "type": "trinket", "rarity": "uncommon"}
    )
    assert path.exists()
    data = loader.load(path)
    assert any("item" in e for e in data["entries"])
