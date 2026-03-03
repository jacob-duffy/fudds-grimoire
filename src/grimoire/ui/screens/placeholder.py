"""Placeholder screen for Fudd's Grimoire."""

from textual.app import ComposeResult
from textual.containers import Middle
from textual.screen import Screen
from textual.widgets import Footer, Header, Label


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
