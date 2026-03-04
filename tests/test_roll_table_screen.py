"""Tests for the Roll Table screen (RollTableScreen)."""

from pathlib import Path

import yaml
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, ListView, Select

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import _TABLE_SCHEMA_COMMENT, LootTableLoader
from grimoire.ui.screens.roll_table import RollTableScreen
from grimoire.ui.widgets import ItemCard

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(
    table_loader: LootTableLoader,
    catalog_loader: ItemCatalogLoader | None = None,
) -> App:
    """Return a minimal App that immediately pushes RollTableScreen."""

    class _Base(Screen):
        def compose(self) -> ComposeResult:
            yield Label("base")

    class _TestApp(App):
        CSS = ""
        SCREENS = {"base": _Base}

        def on_mount(self) -> None:
            self.push_screen(
                RollTableScreen(
                    table_loader=table_loader,
                    catalog_loader=catalog_loader or ItemCatalogLoader(),
                )
            )

    return _TestApp()


def _write_table(path: Path, table_id: str, entries: list, rolls=None) -> None:
    data: dict = {"id": table_id, "entries": entries}
    if rolls is not None:
        data["rolls"] = rolls
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(_TABLE_SCHEMA_COMMENT)
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


def _write_catalog_weapon(loader: ItemCatalogLoader, item_id: str, name: str) -> None:
    loader.save_item(
        "weapon",
        item_id,
        {"name": name, "type": "weapon", "rarity": "common", "value_gp": 10},
    )


# ---------------------------------------------------------------------------
# Mount & initial state
# ---------------------------------------------------------------------------


async def test_screen_mounts_no_tables(tmp_path):
    """Screen mounts without error when no tables exist."""
    loader = LootTableLoader(data_dir=tmp_path / "empty")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        assert app.screen is not None


async def test_no_tables_disables_roll_button(tmp_path):
    """Roll button is disabled when no table files are found."""
    loader = LootTableLoader(data_dir=tmp_path / "empty")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        btn = app.screen.query_one("#btn-roll", Button)
        assert btn.disabled is True


async def test_no_tables_shows_status_message(tmp_path):
    """A helpful status message is shown when no tables exist."""
    loader = LootTableLoader(data_dir=tmp_path / "empty")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert "No tables found" in str(status._Static__content)


async def test_tables_present_enables_roll_button(tmp_path):
    """Roll button is enabled when at least one table file exists."""
    _write_table(
        tmp_path / "t.yml",
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        btn = app.screen.query_one("#btn-roll", Button)
        assert btn.disabled is False


async def test_initial_placeholder_visible(tmp_path):
    """Result placeholder label is visible on first mount."""
    _write_table(
        tmp_path / "t.yml",
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        placeholder = app.screen.query_one("#hint-label", Label)
        assert placeholder.display is True


async def test_initial_items_list_hidden(tmp_path):
    """Items list is hidden before any table is selected."""
    _write_table(
        tmp_path / "t.yml",
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is False


async def test_initial_item_card_hidden(tmp_path):
    """Item card is hidden before any table is selected."""
    _write_table(
        tmp_path / "t.yml",
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        card = app.screen.query_one(ItemCard)
        assert card.display is False


# ---------------------------------------------------------------------------
# Selecting a table populates the items list
# ---------------------------------------------------------------------------


async def test_selecting_table_populates_list(tmp_path):
    """Choosing a table immediately fills the items list with its entries."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [
            {"item": {"name": "Sword", "type": "weapon"}, "weight": 1},
            {"item": {"name": "Shield", "type": "armor"}, "weight": 1},
        ],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is True
        assert len(items_list) == 2


async def test_selecting_table_hides_list_placeholder(tmp_path):
    """The list placeholder is hidden once a table with entries is loaded."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        placeholder = app.screen.query_one("#list-placeholder", Label)
        assert placeholder.display is False


# ---------------------------------------------------------------------------
# Roll — no table selected
# ---------------------------------------------------------------------------


async def test_roll_without_selection_shows_error(tmp_path):
    """Pressing Roll with no table selected shows a status-bar message."""
    _write_table(
        tmp_path / "t.yml",
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        # Force the selector back to blank so nothing is chosen.
        app.screen.query_one("#table-select", Select).clear()
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert str(status._Static__content).strip() != ""
        card = app.screen.query_one(ItemCard)
        assert card.display is False


# ---------------------------------------------------------------------------
# Roll — inline item
# ---------------------------------------------------------------------------


async def test_roll_inline_item_shows_card(tmp_path):
    """Rolling a table with an inline item shows the item card."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item": {"name": "Magic Gem", "type": "gem", "rarity": "rare"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        card = app.screen.query_one(ItemCard)
        assert card.display is True


async def test_roll_via_keyboard_shortcut(tmp_path):
    """Ctrl+R triggers a roll the same way the button does."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item": {"name": "Dagger", "type": "weapon"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.press("ctrl+r")
        await pilot.pause()
        card = app.screen.query_one(ItemCard)
        assert card.display is True


# ---------------------------------------------------------------------------
# Roll — table with no entries
# ---------------------------------------------------------------------------


async def test_roll_empty_table_shows_error(tmp_path):
    """Rolling a table that has no entries shows an error message."""
    table_path = tmp_path / "t.yml"
    _write_table(table_path, "empty_table", [])
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert str(status._Static__content).strip() != ""
        card = app.screen.query_one(ItemCard)
        assert card.display is False


# ---------------------------------------------------------------------------
# Escape returns to previous screen
# ---------------------------------------------------------------------------


async def test_escape_pops_screen(tmp_path):
    """Pressing Escape dismisses RollTableScreen."""
    from grimoire.app import GrimoireApp
    from grimoire.ui.screens import MainMenuScreen

    app = GrimoireApp()
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#menu-roll-table")
        await pilot.pause()
        assert isinstance(app.screen, RollTableScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainMenuScreen)


# ---------------------------------------------------------------------------
# Item card content
# ---------------------------------------------------------------------------


async def test_result_card_shows_item_name(tmp_path):
    """The item card #card-name label shows the rolled item's name."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [
            {
                "item": {"name": "Ancient Shield", "type": "shield", "rarity": "rare"},
                "weight": 1,
            }
        ],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        card_name = app.screen.query_one(".card-name", Label)
        assert "Ancient Shield" in str(card_name._Static__content)


async def test_card_shows_type_rarity_value(tmp_path):
    """The item card displays type, rarity, and value fields."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [
            {
                "item": {
                    "name": "Ruby",
                    "type": "gem",
                    "rarity": "uncommon",
                    "value_gp": 50,
                },
                "weight": 1,
            }
        ],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert "gem" in str(app.screen.query_one(".card-type", Label)._Static__content)
        assert "uncommon" in str(
            app.screen.query_one(".card-rarity", Label)._Static__content
        )
        assert "50" in str(app.screen.query_one(".card-value", Label)._Static__content)


async def test_table_info_label_updated_after_roll(tmp_path):
    """The table info label shows the table ID after a successful roll."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "dungeon_chest",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        info = app.screen.query_one("#table-info", Label)
        assert "dungeon_chest" in str(info._Static__content)


# ---------------------------------------------------------------------------
# Changing table resets card and list
# ---------------------------------------------------------------------------


async def test_switching_table_clears_card(tmp_path):
    """Selecting a different table hides the detail card."""
    table_a = tmp_path / "a.yml"
    table_b = tmp_path / "b.yml"
    _write_table(
        table_a,
        "table_a",
        [{"item": {"name": "Sword", "type": "weapon"}, "weight": 1}],
    )
    _write_table(
        table_b,
        "table_b",
        [{"item": {"name": "Shield", "type": "armor"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_a)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert app.screen.query_one(ItemCard).display is True
        # Switch to the other table → card must be hidden again.
        app.screen.query_one("#table-select", Select).value = str(table_b)
        await pilot.pause()
        assert app.screen.query_one(ItemCard).display is False


# ---------------------------------------------------------------------------
# item_ref resolution
# ---------------------------------------------------------------------------


async def test_item_ref_appears_in_list(tmp_path):
    """An item_ref entry appears in the items list under the catalog item's name."""
    catalog_loader = ItemCatalogLoader(data_dir=tmp_path / "items")
    _write_catalog_weapon(catalog_loader, "iron_sword", "Iron Sword")

    table_path = tmp_path / "tables" / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item_ref": "iron_sword", "weight": 1}],
    )
    table_loader = LootTableLoader(data_dir=tmp_path / "tables")
    app = _make_app(table_loader, catalog_loader=catalog_loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is True
        # The single ListItem's label should contain the catalog item name.
        item_labels = items_list.query("ListItem Label")
        texts = [str(lbl._Static__content) for lbl in item_labels]
        assert any("Iron Sword" in t for t in texts)


async def test_item_ref_resolved_in_card_after_roll(tmp_path):
    """Rolling a table with an item_ref entry resolves the name in the card."""
    catalog_loader = ItemCatalogLoader(data_dir=tmp_path / "items")
    _write_catalog_weapon(catalog_loader, "iron_sword", "Iron Sword")

    table_path = tmp_path / "tables" / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item_ref": "iron_sword", "weight": 1}],
    )
    table_loader = LootTableLoader(data_dir=tmp_path / "tables")
    app = _make_app(table_loader, catalog_loader=catalog_loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        card_name = app.screen.query_one(".card-name", Label)
        assert "Iron Sword" in str(card_name._Static__content)


# ---------------------------------------------------------------------------
# Clearing the table selector restores empty state
# ---------------------------------------------------------------------------


async def test_clearing_selector_hides_items_list(tmp_path):
    """Going back to a blank selection hides the items list and restores placeholder."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item": {"name": "Gem", "type": "gem"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        # First select the table so the list is populated.
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        assert app.screen.query_one("#items-list", ListView).display is True
        # Now clear the selector → list should vanish, placeholder re-appear.
        app.screen.query_one("#table-select", Select).clear()
        await pilot.pause()
        assert app.screen.query_one("#items-list", ListView).display is False
        assert app.screen.query_one("#list-placeholder", Label).display is True


# ---------------------------------------------------------------------------
# Reference entry type
# ---------------------------------------------------------------------------


async def test_reference_entry_shows_stub_when_table_not_found(tmp_path):
    """A 'reference' entry whose table file doesn’t exist shows a stub in the list."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"reference": "other_table", "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is True
        item_labels = items_list.query("ListItem Label")
        texts = [str(lbl._Static__content) for lbl in item_labels]
        assert any("other_table" in t for t in texts)


async def test_reference_entry_expanded_recursively(tmp_path):
    """Items from a referenced table are inlined into the parent list."""
    # Create a sub-table file in the same directory.
    _write_table(
        tmp_path / "sub.yml",
        "sub_table",
        [
            {"item": {"name": "Gem", "type": "gem"}, "weight": 1},
            {"item": {"name": "Coin", "type": "currency"}, "weight": 1},
        ],
    )
    # Parent table references the sub-table.
    _write_table(
        tmp_path / "parent.yml",
        "parent_table",
        [{"reference": "sub_table", "weight": 2}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(
            tmp_path / "parent.yml"
        )
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is True
        item_labels = items_list.query("ListItem Label")
        texts = [str(lbl._Static__content) for lbl in item_labels]
        # Both sub-table items should appear directly in the parent list.
        assert any("Gem" in t for t in texts)
        assert any("Coin" in t for t in texts)
        # No stub names should remain.
        assert not any("[Table:" in t for t in texts)


async def test_reference_cycle_shows_stub(tmp_path):
    """A self-referential table terminates gracefully and shows a stub entry."""
    _write_table(
        tmp_path / "loop.yml",
        "looping",
        [{"reference": "looping", "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(tmp_path / "loop.yml")
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        assert items_list.display is True
        item_labels = items_list.query("ListItem Label")
        texts = [str(lbl._Static__content) for lbl in item_labels]
        assert any("looping" in t for t in texts)


async def test_reference_roll_resolves_to_sub_table_item(tmp_path):
    """Pressing Roll on a table with a reference resolves to an actual subtable item."""
    _write_table(
        tmp_path / "sub.yml",
        "sub_table",
        [{"item": {"name": "Shadow Gem", "type": "gem"}, "weight": 1}],
    )
    _write_table(
        tmp_path / "parent.yml",
        "parent_table",
        [{"reference": "sub_table", "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(
            tmp_path / "parent.yml"
        )
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        card_name = app.screen.query_one(".card-name", Label)
        assert "Shadow Gem" in str(card_name._Static__content)


# ---------------------------------------------------------------------------
# Item description shown in card
# ---------------------------------------------------------------------------


async def test_card_shows_description_when_present(tmp_path):
    """
    The card description label is visible and populated when an item has a description.
    """
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [
            {
                "item": {
                    "name": "Enchanted Orb",
                    "type": "wondrous",
                    "rarity": "rare",
                    "description": "Glows faintly in the dark.",
                },
                "weight": 1,
            }
        ],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        desc_label = app.screen.query_one(".card-desc", Label)
        assert desc_label.display is True
        assert "Glows faintly" in str(desc_label._Static__content)


async def test_card_description_hidden_when_absent(tmp_path):
    """The card description label is hidden when the item has no description."""
    table_path = tmp_path / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item": {"name": "Plain Sword", "type": "weapon"}, "weight": 1}],
    )
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        desc_label = app.screen.query_one(".card-desc", Label)
        assert desc_label.display is False


# ---------------------------------------------------------------------------
# Table info with description field
# ---------------------------------------------------------------------------


async def test_table_info_includes_table_description(tmp_path):
    """The table info label includes the table's own description when set."""
    table_path = tmp_path / "t.yml"
    data: dict = {
        "id": "treasure_chest",
        "description": "Found in the dungeon depths",
        "entries": [{"item": {"name": "Gold Coin", "type": "currency"}, "weight": 1}],
    }
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with open(table_path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh)
    loader = LootTableLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        info = app.screen.query_one("#table-info", Label)
        assert "dungeon depths" in str(info._Static__content)


# ---------------------------------------------------------------------------
# Unresolved item_ref falls back to id stub
# ---------------------------------------------------------------------------


async def test_unresolved_item_ref_shows_stub_name(tmp_path):
    """An item_ref that isn't in the catalog shows the raw id as the name."""
    # Empty catalog — no items defined.
    catalog_loader = ItemCatalogLoader(data_dir=tmp_path / "items")

    table_path = tmp_path / "tables" / "t.yml"
    _write_table(
        table_path,
        "test_table",
        [{"item_ref": "missing_item", "weight": 1}],
    )
    table_loader = LootTableLoader(data_dir=tmp_path / "tables")
    app = _make_app(table_loader, catalog_loader=catalog_loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#table-select", Select).value = str(table_path)
        await pilot.pause()
        items_list = app.screen.query_one("#items-list", ListView)
        item_labels = items_list.query("ListItem Label")
        texts = [str(lbl._Static__content) for lbl in item_labels]
        assert any("missing_item" in t for t in texts)
