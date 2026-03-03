"""Fudd's Grimoire — main Textual application."""

from textual.app import App

from grimoire.ui.screens import MainMenuScreen


class GrimoireApp(App):
    """The main TUI application for Fudd's Grimoire."""

    TITLE = "Fudd's Grimoire"
    SUB_TITLE = "Loot Table Manager"

    SCREENS = {
        "main_menu": MainMenuScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("main_menu")
