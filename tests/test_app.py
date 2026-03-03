"""Tests for the GrimoireApp Textual application."""

from textual.widgets import Footer, Header, Label, ListView

from grimoire.app import GrimoireApp
from grimoire.ui.screens import (
    AddItemScreen,
    MainMenuScreen,
    PlaceholderScreen,
    RollItemScreen,
)


def test_app_title():
    """GrimoireApp should have the correct title and subtitle."""
    app = GrimoireApp()
    assert app.TITLE == "Fudd's Grimoire"
    assert app.SUB_TITLE == "Loot Table Manager"


def test_app_registers_main_menu_screen():
    """GrimoireApp should register MainMenuScreen under 'main_menu'."""
    app = GrimoireApp()
    assert "main_menu" in app.SCREENS
    assert app.SCREENS["main_menu"] is MainMenuScreen


def test_main_menu_has_four_options():
    """MainMenuScreen should define exactly four menu options."""
    assert len(MainMenuScreen.MENU_OPTIONS) == 4


def test_main_menu_option_labels():
    """MainMenuScreen menu options should include all expected actions."""
    labels = [label for _, label in MainMenuScreen.MENU_OPTIONS]
    assert "Add New Item" in labels
    assert "Add New Table" in labels
    assert "Roll Table" in labels
    assert "Roll Item" in labels


async def test_main_menu_screen_mounts():
    """MainMenuScreen should render the menu list and title when mounted."""
    app = GrimoireApp()
    async with app.run_test():
        assert isinstance(app.screen, MainMenuScreen)
        assert app.screen.query_one("#main-menu", ListView) is not None
        assert app.screen.query_one("#menu-title", Label) is not None
        assert app.screen.query_one(Header) is not None
        assert app.screen.query_one(Footer) is not None


async def test_placeholder_screen_widgets():
    """PlaceholderScreen should render its title, body, Header and Footer."""
    app = GrimoireApp()
    async with app.run_test() as pilot:
        await pilot.click("#menu-add-table")
        assert isinstance(app.screen, PlaceholderScreen)
        assert app.screen._screen_title == "Add New Table"
        assert app.screen.query_one("#placeholder-body", Label) is not None
        assert app.screen.query_one(Header) is not None
        assert app.screen.query_one(Footer) is not None


async def test_placeholder_back_returns_to_main_menu():
    """Pressing Escape from a placeholder screen should return to MainMenuScreen."""
    app = GrimoireApp()
    async with app.run_test() as pilot:
        await pilot.click("#menu-add-table")
        assert isinstance(app.screen, PlaceholderScreen)
        await pilot.press("escape")
        assert isinstance(app.screen, MainMenuScreen)


async def test_add_item_menu_navigates_to_add_item_screen():
    """Clicking 'Add New Item' should push AddItemScreen."""
    app = GrimoireApp()
    async with app.run_test() as pilot:
        await pilot.click("#menu-add-item")
        assert isinstance(app.screen, AddItemScreen)


async def test_all_menu_items_navigate_to_expected_screens():
    """Each menu item pushes the correct screen type."""
    expected = {
        "menu-add-item": AddItemScreen,
        "menu-add-table": PlaceholderScreen,
        "menu-roll-table": PlaceholderScreen,
        "menu-roll-item": RollItemScreen,
    }
    for item_id, screen_type in expected.items():
        app = GrimoireApp()
        async with app.run_test() as pilot:
            await pilot.click(f"#{item_id}")
            assert isinstance(app.screen, screen_type)
            await pilot.press("escape")
            assert isinstance(app.screen, MainMenuScreen)
