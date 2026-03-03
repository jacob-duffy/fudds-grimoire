"""Tests for the Add New Item screen (AddItemScreen)."""

from pathlib import Path

import pytest
import yaml
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Select, Switch

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import _TABLE_SCHEMA_COMMENT, LootTableLoader
from grimoire.models.item import SUBFORM_IDS
from grimoire.ui.add_item import AddItemScreen, _num

# ---------------------------------------------------------------------------
# _num() helper unit tests
# ---------------------------------------------------------------------------


def test_num_whole_number_returns_int():
    assert _num("5") == 5
    assert isinstance(_num("5"), int)


def test_num_zero_returns_int():
    assert _num("0") == 0
    assert isinstance(_num("0"), int)


def test_num_fractional_returns_float():
    assert _num("0.5") == 0.5
    assert isinstance(_num("0.5"), float)


def test_num_large_whole_number_returns_int():
    assert _num("1000") == 1000
    assert isinstance(_num("1000"), int)


def test_num_invalid_raises_value_error():
    with pytest.raises(ValueError):
        _num("abc")


# ---------------------------------------------------------------------------
# Test app helper
# ---------------------------------------------------------------------------


def _write_table(path: Path, table_id: str) -> None:
    data = {"id": table_id, "entries": [{"item_ref": "iron_sword", "weight": 1}]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write(_TABLE_SCHEMA_COMMENT)
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


def _make_app(
    loader: ItemCatalogLoader,
    table_loader: LootTableLoader | None = None,
) -> App:
    """Return a minimal App that pushes AddItemScreen with injected loaders."""

    class _Base(Screen):
        def compose(self) -> ComposeResult:
            yield Label("base")

    class _TestApp(App):
        CSS = ""
        SCREENS = {"base": _Base}

        def on_mount(self) -> None:
            self.push_screen(AddItemScreen(loader=loader, table_loader=table_loader))

    return _TestApp()


# ---------------------------------------------------------------------------
# Mount & initial state
# ---------------------------------------------------------------------------


async def test_add_item_screen_mounts(tmp_path):
    """AddItemScreen renders required fields, table select, and action buttons."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test():
        assert isinstance(app.screen, AddItemScreen)
        assert app.screen.query_one("#field-type", Select) is not None
        assert app.screen.query_one("#field-name", Input) is not None
        assert app.screen.query_one("#field-rarity", Select) is not None
        assert app.screen.query_one("#field-table", Select) is not None
        assert app.screen.query_one("#field-rarity", Select) is not None
        assert app.screen.query_one("#btn-save") is not None
        assert app.screen.query_one("#btn-cancel") is not None


async def test_subforms_hidden_initially(tmp_path):
    """All type-specific sub-forms are hidden when the screen first mounts."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test():
        for sf in SUBFORM_IDS:
            assert not app.screen.query_one(f"#subform-{sf}").display


async def test_attunement_req_row_hidden_initially(tmp_path):
    """The attunement requirements row is hidden before the switch is toggled."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test():
        assert not app.screen.query_one("#row-attunement-req").display


# ---------------------------------------------------------------------------
# Sub-form visibility
# ---------------------------------------------------------------------------


async def test_weapon_type_shows_weapon_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "weapon"
        await pilot.pause()
        assert app.screen.query_one("#subform-weapon").display
        for sf in SUBFORM_IDS:
            if sf != "weapon":
                assert not app.screen.query_one(f"#subform-{sf}").display


async def test_armor_type_shows_armor_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "armor"
        await pilot.pause()
        assert app.screen.query_one("#subform-armor").display


async def test_shield_type_shows_armor_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "shield"
        await pilot.pause()
        assert app.screen.query_one("#subform-armor").display


async def test_potion_type_shows_consumable_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "potion"
        await pilot.pause()
        assert app.screen.query_one("#subform-consumable").display


async def test_wand_type_shows_wondrous_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "wand"
        await pilot.pause()
        assert app.screen.query_one("#subform-wondrous").display


async def test_currency_type_shows_currency_subform(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "currency"
        await pilot.pause()
        assert app.screen.query_one("#subform-currency").display


async def test_trinket_type_hides_all_subforms(tmp_path):
    """Types with no sub-form entry hide all sub-form sections."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        for sf in SUBFORM_IDS:
            assert not app.screen.query_one(f"#subform-{sf}").display


# ---------------------------------------------------------------------------
# Attunement toggle
# ---------------------------------------------------------------------------


async def test_attunement_toggle_shows_requirements(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-attunement", Switch).value = True
        await pilot.pause()
        assert app.screen.query_one("#row-attunement-req").display


async def test_attunement_toggle_off_hides_requirements(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-attunement", Switch).value = True
        await pilot.pause()
        app.screen.query_one("#field-attunement", Switch).value = False
        await pilot.pause()
        assert not app.screen.query_one("#row-attunement-req").display


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


async def test_validation_shows_error_when_all_required_missing(tmp_path):
    """Clicking Save with no required fields filled stays on AddItemScreen."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        await pilot.click("#btn-save")
        await pilot.pause()
        # Screen did not navigate away; no file was created
        assert isinstance(app.screen, AddItemScreen)
        assert not any(tmp_path.iterdir())


async def test_validation_shows_error_when_name_missing(tmp_path):
    """Clicking Save without a name stays on AddItemScreen and writes no file."""
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        app.screen.query_one("#field-type", Select).value = "weapon"
        app.screen.query_one("#field-rarity", Select).value = "common"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert isinstance(app.screen, AddItemScreen)
        assert not (tmp_path / "weapons.yml").exists()


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------


async def test_cancel_pops_screen(tmp_path):
    app = _make_app(ItemCatalogLoader(data_dir=tmp_path))
    async with app.run_test() as pilot:
        await pilot.click("#btn-cancel")
        await pilot.pause()
        assert not isinstance(app.screen, AddItemScreen)


# ---------------------------------------------------------------------------
# Successful saves
# ---------------------------------------------------------------------------


async def test_save_weapon(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "weapon"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Iron Sword"
        s.query_one("#field-rarity", Select).value = "common"
        s.query_one("#field-weapon-dice", Input).value = "1d8"
        s.query_one("#field-weapon-dmg-type", Select).value = "slashing"
        s.query_one("#field-weapon-props", Input).value = "versatile, light"
        s.query_one("#field-weapon-range-normal", Input).value = "5"
        s.query_one("#field-weapon-range-long", Input).value = "10"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("weapon")
    item = catalog["items"]["iron_sword"]
    assert item["name"] == "Iron Sword"
    assert item["weapon"]["damage"] == {"dice": "1d8", "type": "slashing"}
    assert "versatile" in item["weapon"]["properties"]
    assert item["weapon"]["range_normal_ft"] == 5


async def test_save_armor(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "armor"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Chain Mail"
        s.query_one("#field-rarity", Select).value = "common"
        s.query_one("#field-armor-base-ac", Input).value = "16"
        s.query_one("#field-armor-dex-bonus", Select).value = "none"
        s.query_one("#field-armor-str-req", Input).value = "13"
        s.query_one("#field-armor-stealth", Switch).value = True
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("armor")
    item = catalog["items"]["chain_mail"]
    assert item["armor"]["base_ac"] == 16
    assert item["armor"]["dex_bonus"] == "none"
    assert item["armor"]["strength_requirement"] == 13
    assert item["armor"]["stealth_disadvantage"] is True


async def test_save_consumable(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "potion"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Potion of Healing"
        s.query_one("#field-rarity", Select).value = "common"
        s.query_one("#field-consumable-charges", Input).value = "1"
        s.query_one("#field-consumable-spell", Input).value = "Cure Wounds"
        s.query_one("#field-consumable-spell-level", Input).value = "1"
        s.query_one("#field-consumable-healing", Input).value = "2d4+2"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("potion")
    item = catalog["items"]["potion_of_healing"]
    assert item["consumable"]["charges"] == 1
    assert item["consumable"]["spell"] == "Cure Wounds"
    assert item["consumable"]["healing_dice"] == "2d4+2"


async def test_save_wondrous(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "wand"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Wand of Fireballs"
        s.query_one("#field-rarity", Select).value = "rare"
        s.query_one("#field-wondrous-charges", Input).value = "7"
        s.query_one("#field-wondrous-recharge", Input).value = "1d6+1"
        s.query_one("#field-wondrous-activation", Select).value = "action"
        s.query_one("#field-wondrous-effects", Input).value = (
            "Fireball (1 charge), Scorching Ray (2 charges)"
        )
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("wand")
    item = catalog["items"]["wand_of_fireballs"]
    assert item["wondrous"]["charges"] == 7
    assert item["wondrous"]["recharge"] == "1d6+1"
    assert item["wondrous"]["activation"] == "action"
    assert "Fireball (1 charge)" in item["wondrous"]["effects"]


async def test_save_currency(tmp_path):
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "currency"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Gold Piece"
        s.query_one("#field-rarity", Select).value = "common"
        s.query_one("#field-currency-denom", Select).value = "gp"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("currency")
    item = catalog["items"]["gold_piece"]
    assert item["currency"]["denomination"] == "gp"


async def test_save_trinket_no_subform(tmp_path):
    """Types without a sub-form are saved with only the base fields."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Lucky Pebble"
        s.query_one("#field-rarity", Select).value = "common"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("trinket")
    assert "lucky_pebble" in catalog["items"]


async def test_save_with_optional_fields(tmp_path):
    """Optional fields (description, value_gp, weight_lb, magical,
    tags, source) are saved."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Mystic Orb"
        s.query_one("#field-rarity", Select).value = "uncommon"
        s.query_one("#field-description", Input).value = "A glowing sphere."
        s.query_one("#field-value-gp", Input).value = "150"
        s.query_one("#field-weight-lb", Input).value = "0.5"
        s.query_one("#field-magical", Switch).value = True
        s.query_one("#field-tags", Input).value = "light, arcane"
        s.query_one("#field-source", Input).value = "homebrew"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("trinket")
    item = catalog["items"]["mystic_orb"]
    assert item["description"] == "A glowing sphere."
    assert item["value_gp"] == 150
    assert isinstance(item["value_gp"], int)
    assert item["weight_lb"] == 0.5
    assert isinstance(item["weight_lb"], float)
    assert item["magical"] is True
    assert "light" in item["tags"]
    assert item["source"] == "homebrew"


async def test_save_with_attunement(tmp_path):
    """Attunement flag and optional requirements are saved correctly."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "ring"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Ring of Evasion"
        s.query_one("#field-rarity", Select).value = "rare"
        s.query_one("#field-attunement", Switch).value = True
        await pilot.pause()
        s.query_one("#field-attunement-req", Input).value = "by a rogue"
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("ring")
    item = catalog["items"]["ring_of_evasion"]
    assert item["attunement"] is True
    assert item["attunement_requirements"] == "by a rogue"


async def test_ctrl_s_saves(tmp_path):
    """The Ctrl+S binding triggers the same save logic as the Save button."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test() as pilot:
        s = app.screen
        s.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Bone Dice"
        s.query_one("#field-rarity", Select).value = "common"
        await pilot.press("ctrl+s")
        await pilot.pause()

    assert "bone_dice" in loader.load("trinket")["items"]


# ---------------------------------------------------------------------------
# Table-linking tests
# ---------------------------------------------------------------------------


async def test_table_select_disabled_when_no_table_loader(tmp_path):
    """Table select is disabled when no table_loader is provided."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader, table_loader=None)
    async with app.run_test() as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#field-table", Select)
        assert sel.disabled


async def test_table_select_disabled_when_tables_dir_empty(tmp_path):
    """Table select is disabled when tables dir exists but has no yml files."""
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    loader = ItemCatalogLoader(data_dir=tmp_path)
    table_loader = LootTableLoader(data_dir=tables_dir)
    app = _make_app(loader, table_loader=table_loader)
    async with app.run_test() as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#field-table", Select)
        assert sel.disabled


async def test_table_select_populated_from_directory(tmp_path):
    """Table select shows available tables once they exist in the tables dir."""
    tables_dir = tmp_path / "tables"
    _write_table(tables_dir / "dungeon.yml", "dungeon_loot")
    _write_table(tables_dir / "forest.yml", "forest_loot")
    loader = ItemCatalogLoader(data_dir=tmp_path)
    table_loader = LootTableLoader(data_dir=tables_dir)
    app = _make_app(loader, table_loader=table_loader)
    async with app.run_test() as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#field-table", Select)
        assert not sel.disabled
        # _table_paths should have an entry for each table
        assert len(app.screen._table_paths) == 2


async def test_save_inline_to_table(tmp_path):
    """When a table is selected, item is appended as inline entry to that table."""
    tables_dir = tmp_path / "tables"
    table_file = tables_dir / "forest.yml"
    _write_table(table_file, "forest_loot")

    loader = ItemCatalogLoader(data_dir=tmp_path)
    table_loader = LootTableLoader(data_dir=tables_dir)
    app = _make_app(loader, table_loader=table_loader)

    async with app.run_test() as pilot:
        s = app.screen
        await pilot.pause()
        s.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Forest Charm"
        s.query_one("#field-rarity", Select).value = "common"
        # select the first (only) table key
        table_key = next(iter(s._table_paths))
        s.query_one("#field-table", Select).value = table_key
        await pilot.click("#btn-save")
        await pilot.pause()

    # Item should NOT be in the catalog
    catalog = loader.load("trinket")
    assert "forest_charm" not in catalog.get("items", {})

    # Item SHOULD appear as an inline entry in the table file
    table_data = table_loader.load(table_file)
    names = [
        e.get("item", {}).get("name")
        for e in table_data.get("entries", [])
        if "item" in e
    ]
    assert "Forest Charm" in names


async def test_save_to_catalog_when_no_table_selected(tmp_path):
    """When no table is selected, item is saved to the catalog as normal."""
    tables_dir = tmp_path / "tables"
    table_file = tables_dir / "treasure.yml"
    _write_table(table_file, "treasure_loot")

    loader = ItemCatalogLoader(data_dir=tmp_path)
    table_loader = LootTableLoader(data_dir=tables_dir)
    app = _make_app(loader, table_loader=table_loader)

    async with app.run_test() as pilot:
        s = app.screen
        await pilot.pause()
        s.query_one("#field-type", Select).value = "trinket"
        await pilot.pause()
        s.query_one("#field-name", Input).value = "Plain Stone"
        s.query_one("#field-rarity", Select).value = "common"
        # leave #field-table unselected (BLANK)
        await pilot.click("#btn-save")
        await pilot.pause()

    catalog = loader.load("trinket")
    assert "plain_stone" in catalog["items"]

    # Table file should still only have the original iron_sword ref entry
    table_data = table_loader.load(table_file)
    inline = [e for e in table_data.get("entries", []) if "item" in e]
    assert len(inline) == 0
