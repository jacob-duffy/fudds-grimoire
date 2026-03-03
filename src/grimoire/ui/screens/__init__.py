"""Textual screens for Fudd's Grimoire.

All screens are re-exported here so consumers can import from a single path:

    from grimoire.ui.screens import AddItemScreen, MainMenuScreen, ...
"""

from grimoire.ui.screens.add_item import AddItemScreen
from grimoire.ui.screens.main_menu import MainMenuScreen
from grimoire.ui.screens.placeholder import PlaceholderScreen
from grimoire.ui.screens.roll_item import RollItemScreen

__all__ = [
    "AddItemScreen",
    "MainMenuScreen",
    "PlaceholderScreen",
    "RollItemScreen",
]
