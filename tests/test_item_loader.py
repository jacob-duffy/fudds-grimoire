"""Tests for grimoire.loaders.items.ItemCatalogLoader."""

from grimoire.loaders.items import _SCHEMA_COMMENT, ItemCatalogLoader

# -- load ---------------------------------------------------------------------


def test_load_nonexistent_file(tmp_path):
    """Loading from a missing file returns an empty catalog."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    result = loader.load("weapon")
    assert result == {"items": {}}


def test_load_existing_file(tmp_path):
    """A valid YAML file is parsed and returned."""
    (tmp_path / "weapons.yml").write_text(
        _SCHEMA_COMMENT
        + "items:\n"
        + "  iron_sword:\n"
        + "    name: Iron Sword\n"
        + "    type: weapon\n"
        + "    rarity: common\n"
    )
    loader = ItemCatalogLoader(data_dir=tmp_path)
    result = loader.load("weapon")
    assert "iron_sword" in result["items"]
    assert result["items"]["iron_sword"]["name"] == "Iron Sword"


def test_load_empty_file_returns_empty_catalog(tmp_path):
    """A file that is empty (null) is treated as an empty catalog."""
    (tmp_path / "weapons.yml").write_text("")
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert loader.load("weapon") == {"items": {}}


def test_load_file_without_items_key_returns_empty(tmp_path):
    """A YAML file whose top-level structure lacks 'items' returns empty."""
    (tmp_path / "weapons.yml").write_text("something: else\n")
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert loader.load("weapon") == {"items": {}}


# -- file_for_type ------------------------------------------------------------


def test_file_for_type_weapon(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert loader.file_for_type("weapon") == tmp_path / "weapons.yml"


def test_file_for_type_unknown_falls_back_to_items(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert loader.file_for_type("unknown_type") == tmp_path / "items.yml"


def test_file_for_type_currency(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    assert loader.file_for_type("currency") == tmp_path / "currency.yml"


# -- save_item ----------------------------------------------------------------


def test_save_creates_file(tmp_path):
    """save_item creates the YAML file if it does not exist."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    item = {"name": "Iron Sword", "type": "weapon", "rarity": "common"}
    path = loader.save_item("weapon", "iron_sword", item)
    assert path.exists()


def test_save_returns_correct_path(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    path = loader.save_item(
        "weapon", "x", {"name": "X", "type": "weapon", "rarity": "common"}
    )
    assert path == tmp_path / "weapons.yml"


def test_save_writes_schema_comment(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item("weapon", "x", {"name": "X", "type": "weapon", "rarity": "common"})
    content = (tmp_path / "weapons.yml").read_text()
    assert _SCHEMA_COMMENT.strip() in content


def test_save_item_is_retrievable(tmp_path):
    """An item saved via save_item can be loaded back correctly."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    item = {"name": "Flame Tongue", "type": "weapon", "rarity": "rare", "magical": True}
    loader.save_item("weapon", "flame_tongue", item)
    catalog = loader.load("weapon")
    assert catalog["items"]["flame_tongue"]["name"] == "Flame Tongue"
    assert catalog["items"]["flame_tongue"]["magical"] is True


def test_save_appends_to_existing_catalog(tmp_path):
    """Multiple saves to the same file accumulate items."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "weapon", "sword", {"name": "Sword", "type": "weapon", "rarity": "common"}
    )
    loader.save_item(
        "weapon", "axe", {"name": "Axe", "type": "weapon", "rarity": "common"}
    )
    catalog = loader.load("weapon")
    assert "sword" in catalog["items"]
    assert "axe" in catalog["items"]


def test_save_overwrites_existing_id(tmp_path):
    """Saving with an existing ID replaces that item."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "weapon", "sword", {"name": "Old Sword", "type": "weapon", "rarity": "common"}
    )
    loader.save_item(
        "weapon", "sword", {"name": "New Sword", "type": "weapon", "rarity": "rare"}
    )
    catalog = loader.load("weapon")
    assert catalog["items"]["sword"]["name"] == "New Sword"
    assert catalog["items"]["sword"]["rarity"] == "rare"


def test_save_creates_parent_directories(tmp_path):
    """Subdirectories are created automatically."""
    loader = ItemCatalogLoader(data_dir=tmp_path / "deep" / "nested")
    loader.save_item(
        "trinket",
        "shiny_pebble",
        {"name": "Shiny Pebble", "type": "trinket", "rarity": "common"},
    )
    assert (tmp_path / "deep" / "nested" / "trinkets.yml").exists()


def test_save_different_types_to_different_files(tmp_path):
    """Weapons and armour are stored in different catalog files."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "weapon", "sword", {"name": "Sword", "type": "weapon", "rarity": "common"}
    )
    loader.save_item(
        "armor", "plate", {"name": "Plate Mail", "type": "armor", "rarity": "uncommon"}
    )
    assert (tmp_path / "weapons.yml").exists()
    assert (tmp_path / "armor.yml").exists()
