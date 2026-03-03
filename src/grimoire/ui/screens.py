"""Textual screens for Fudd's Grimoire."""

from textual.app import ComposeResult
from textual.containers import Middle
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView


class PlaceholderScreen(Screen):
    """A generic placeholder screen for features not yet implemented."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    DEFAULT_CSS = """
    PlaceholderScreen {
        background: $surface;
    }

    #placeholder-title {
        text-align: center;
        padding: 1 2;
        text-style: bold;
        color: $accent;
        width: 100%;
    }

    #placeholder-body {
        text-align: center;
        color: $text-muted;
        width: 100%;
    }
    """

    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._screen_title = title

    def compose(self) -> ComposeResult:
        yield Header()
        with Middle():
            yield Label(self._screen_title, id="placeholder-title")
            yield Label("Coming soon...", id="placeholder-body")
        yield Footer()


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
            self.app.push_screen(PlaceholderScreen("Add New Item"))
        elif item_id == "menu-add-table":
            self.app.push_screen(PlaceholderScreen("Add New Table"))
        elif item_id == "menu-roll-table":
            self.app.push_screen(PlaceholderScreen("Roll Table"))
        elif item_id == "menu-roll-item":
            self.app.push_screen(PlaceholderScreen("Roll Item"))
