"""Fudd's Grimoire — main Textual application."""

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class GrimoireApp(App):
    """The main TUI application for Fudd's Grimoire."""

    TITLE = "Fudd's Grimoire"
    SUB_TITLE = "Loot Table Manager"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
