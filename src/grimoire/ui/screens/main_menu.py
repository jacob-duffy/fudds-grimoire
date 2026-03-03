"""Main menu screen for Fudd's Grimoire."""

from itertools import islice
from typing import Iterator

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import LootTableLoader
from grimoire.ui.screens.add_item import AddItemScreen
from grimoire.ui.screens.placeholder import PlaceholderScreen
from grimoire.ui.screens.roll_item import RollItemScreen
from grimoire.ui.screens.roll_table import RollTableScreen


class MainMenuScreen(Screen):
    """The main menu screen shown on application start."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
    ]

    # Each section: (section_id, display_title, [(option_id, option_label), ...])
    SECTIONS: list[tuple[str, str, list[tuple[str, str]]]] = [
        (
            "loot",
            "Loot",
            [
                ("add-item", "Add New Item"),
                ("add-table", "Add New Table"),
                ("roll-table", "Roll Table"),
                ("roll-item", "Roll Item"),
            ],
        ),
        (
            "monsters",
            "Monsters",
            [
                ("view-bestiary", "View Bestiary"),
                ("roll-encounter", "Roll Encounter"),
                ("monster-info", "Monster Info"),
            ],
        ),
        (
            "party",
            "Party",
            [
                ("manage-party", "Manage Party"),
                ("track-hp", "Track HP"),
                ("roll-stats", "Roll Stats"),
            ],
        ),
    ]

    _MAX_PER_ROW: int = 5

    # Stores each ListView's index when it loses focus so it can be restored.
    _saved_indices: dict[str, int | None]

    DEFAULT_CSS = """
    MainMenuScreen {
        background: $surface;
    }

    #menu-title {
        text-align: center;
        padding: 1 1;
        text-style: bold;
        color: $accent;
        width: 100%;
    }

    .menu-row {
        height: auto;
        width: 100%;
        align: center top;
        margin-bottom: 1;
    }

    .menu-section {
        width: 32;
        height: auto;
        margin: 0 2;
        padding: 0;
        border-title-align: center;
        border-title-style: bold;
    }

    #section-loot {
        border: solid $primary;
        border-title-color: $primary;
    }

    #section-monsters {
        border: solid $warning;
        border-title-color: $warning;
    }

    #section-party {
        border: solid $success;
        border-title-color: $success;
    }
    """

    @staticmethod
    def _chunked(iterable: list, size: int) -> Iterator[list]:
        """Yield successive chunks of *size* from *iterable*."""
        it = iter(iterable)
        while chunk := list(islice(it, size)):
            yield chunk

    def compose(self) -> ComposeResult:
        yield Header()
        with Middle():
            with Vertical(id="menu-wrapper"):
                yield Label("Welcome to Fudd's Grimoire", id="menu-title")
                for row_idx, row in enumerate(
                    self._chunked(self.SECTIONS, self._MAX_PER_ROW)
                ):
                    with Horizontal(classes="menu-row", id=f"menu-row-{row_idx}"):
                        for section_id, _title, options in row:
                            yield ListView(
                                *[
                                    ListItem(Label(f"  {label}"), id=f"menu-{key}")
                                    for key, label in options
                                ],
                                initial_index=None,
                                id=f"section-{section_id}",
                                classes="menu-section",
                            )
        yield Footer()

    def on_mount(self) -> None:
        """Set border titles and initialise saved-index store."""
        self._saved_indices = {}
        for section_id, title, _options in self.SECTIONS:
            lv = self.query_one(f"#section-{section_id}", ListView)
            lv.border_title = title

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """Clear a ListView's highlight when it loses focus."""
        if isinstance(event.widget, ListView):
            lv = event.widget
            self._saved_indices[lv.id] = lv.index
            lv.index = None

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """Restore a ListView's highlight when it regains focus."""
        if isinstance(event.widget, ListView):
            lv = event.widget
            lv.index = self._saved_indices.get(lv.id, 0)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle menu item selection."""
        item_id = event.item.id

        # --- Loot ---
        if item_id == "menu-add-item":
            self.app.push_screen(AddItemScreen(table_loader=LootTableLoader()))
        elif item_id == "menu-add-table":
            self.app.push_screen(PlaceholderScreen("Add New Table"))
        elif item_id == "menu-roll-table":
            self.app.push_screen(
                RollTableScreen(
                    table_loader=LootTableLoader(),
                    catalog_loader=ItemCatalogLoader(),
                )
            )
        elif item_id == "menu-roll-item":
            self.app.push_screen(RollItemScreen(loader=ItemCatalogLoader()))
        # --- Monsters ---
        elif item_id == "menu-view-bestiary":
            self.app.push_screen(PlaceholderScreen("View Bestiary"))
        elif item_id == "menu-roll-encounter":
            self.app.push_screen(PlaceholderScreen("Roll Encounter"))
        elif item_id == "menu-monster-info":
            self.app.push_screen(PlaceholderScreen("Monster Info"))
        # --- Party ---
        elif item_id == "menu-manage-party":
            self.app.push_screen(PlaceholderScreen("Manage Party"))
        elif item_id == "menu-track-hp":
            self.app.push_screen(PlaceholderScreen("Track HP"))
        elif item_id == "menu-roll-stats":
            self.app.push_screen(PlaceholderScreen("Roll Stats"))
