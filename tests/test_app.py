"""Tests for the GrimoireApp Textual application."""

from textual.widgets import Footer, Header

from grimoire.app import GrimoireApp


def test_app_title():
    """GrimoireApp should have the correct title and subtitle."""
    app = GrimoireApp()
    assert app.TITLE == "Fudd's Grimoire"
    assert app.SUB_TITLE == "Loot Table Manager"


def test_app_compose():
    """compose() should yield a Header followed by a Footer."""
    app = GrimoireApp()
    widgets = list(app.compose())
    assert len(widgets) == 2
    assert isinstance(widgets[0], Header)
    assert isinstance(widgets[1], Footer)
