"""Main menu screen for Fudd's Grimoire."""

from textual.app import ComposeResult
from textual.containers import Middle
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import LootTableLoader
from grimoire.ui.screens.add_item import AddItemScreen
from grimoire.ui.screens.placeholder import PlaceholderScreen
from grimoire.ui.screens.roll_item import RollItemScreen


class MainMenuScreen(Screen):
    """The main menu screen shown on application start."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
    ]

    MENU_OPTIONS = [
        ("add-item", "Add New Item"),
        ("add-table", "Add New Table"),
        ("roll-table", "Roll Table"),
        ("roll-item", "Roll Item"),
    ]

    DEFAULT_CSS = """
    MainMenuScreen {
        background: $surface;
    }

    #menu-title {
        text-align: center;
        padding: 1 2;
        text-style: bold;
        color: $accent;
        width: 100%;
    }

    #main-menu {
        width: 40;
        height: auto;
        border: solid $primary;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Middle():
            yield Label("Welcome to Fudd's Grimoire", id="menu-title")
            yield ListView(
                *[
                    ListItem(Label(f"  {label}"), id=f"menu-{key}")
                    for key, label in self.MENU_OPTIONS
                ],
                id="main-menu",
            )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle menu item selection."""
        item_id = event.item.id

        if item_id == "menu-add-item":
            self.app.push_screen(AddItemScreen(table_loader=LootTableLoader()))
        elif item_id == "menu-add-table":
            self.app.push_screen(PlaceholderScreen("Add New Table"))
        elif item_id == "menu-roll-table":
            self.app.push_screen(PlaceholderScreen("Roll Table"))
        elif item_id == "menu-roll-item":
            self.app.push_screen(RollItemScreen(loader=ItemCatalogLoader()))
