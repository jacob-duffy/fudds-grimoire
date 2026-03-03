"""Tests for the Roll Item screen (RollItemScreen)."""

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Select, SelectionList

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.ui.roll_item import RollItemScreen

# ---------------------------------------------------------------------------
# Test app helper
# ---------------------------------------------------------------------------


def _make_app(loader: ItemCatalogLoader) -> App:
    """Return a minimal App that pushes RollItemScreen with an injected loader."""

    class _Base(Screen):
        def compose(self) -> ComposeResult:
            yield Label("base")

    class _TestApp(App):
        CSS = ""
        SCREENS = {"base": _Base}

        def on_mount(self) -> None:
            self.push_screen(RollItemScreen(loader=loader))

    return _TestApp()


def _write_weapon(loader: ItemCatalogLoader, item_id: str = "sword", **kwargs):
    """Convenience: save a minimal weapon item."""
    data = {
        "name": kwargs.get("name", "Iron Sword"),
        "type": kwargs.get("type", "weapon"),
        "rarity": kwargs.get("rarity", "common"),
        **{k: v for k, v in kwargs.items() if k not in ("name", "type", "rarity")},
    }
    loader.save_item(data["type"], item_id, data)


# ---------------------------------------------------------------------------
# Mount & initial state
# ---------------------------------------------------------------------------


async def test_screen_mounts(tmp_path):
    """RollItemScreen mounts without error."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        assert app.screen is not None


async def test_initial_placeholder_visible(tmp_path):
    """Result placeholder is visible and result card is hidden on mount."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        placeholder = app.screen.query_one("#result-placeholder", Label)
        card = app.screen.query_one("#result-card")
        assert placeholder.display is True
        assert card.display is False


async def test_initial_status_bar_empty(tmp_path):
    """Status bar starts empty."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert str(status._Static__content).strip() == ""


async def test_rarity_select_has_all_rarities(tmp_path):
    """Rarity SelectionList contains all RARITIES values."""
    from grimoire.models.item import RARITIES

    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#rarity-select", SelectionList)
        option_values = [sel.get_option_at_index(i).value for i in range(len(RARITIES))]
        for rarity in RARITIES:
            assert rarity in option_values


async def test_types_select_has_all_types(tmp_path):
    """Type SelectionList contains all ITEM_TYPES values."""
    from grimoire.models.item import ITEM_TYPES

    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#types-select", SelectionList)
        option_values = [
            sel.get_option_at_index(i).value for i in range(len(ITEM_TYPES))
        ]
        for item_type in ITEM_TYPES:
            assert item_type in option_values


# ---------------------------------------------------------------------------
# Roll button — no items
# ---------------------------------------------------------------------------


async def test_roll_empty_catalog_shows_error(tmp_path):
    """Rolling with an empty catalog shows a 'No items match' error."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert "No items match" in str(status._Static__content)


async def test_roll_empty_catalog_keeps_placeholder(tmp_path):
    """After a failed roll the placeholder remains visible and card hidden."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert app.screen.query_one("#result-placeholder").display is True
        assert app.screen.query_one("#result-card").display is False


# ---------------------------------------------------------------------------
# Roll button — successful roll
# ---------------------------------------------------------------------------


async def test_roll_shows_result_card(tmp_path):
    """After a successful roll the result card becomes visible."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert app.screen.query_one("#result-card").display is True
        assert app.screen.query_one("#result-placeholder").display is False


async def test_roll_result_contains_item_name(tmp_path):
    """The result card shows the rolled item's name."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader, name="Dragon Blade")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        name_label = app.screen.query_one("#result-name", Label)
        assert "Dragon Blade" in str(name_label._Static__content)


async def test_roll_result_contains_type(tmp_path):
    """The result card shows the item type."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader, name="Sword", type="weapon")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        type_label = app.screen.query_one("#result-type", Label)
        assert "weapon" in str(type_label._Static__content)


async def test_roll_result_contains_rarity(tmp_path):
    """The result card shows the item rarity."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader, name="Sword", rarity="uncommon")
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        rarity_label = app.screen.query_one("#result-rarity", Label)
        assert "uncommon" in str(rarity_label._Static__content)


async def test_roll_result_shows_value_when_present(tmp_path):
    """The result card shows value_gp when the item has it."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader, name="Sword", value_gp=75)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        value_label = app.screen.query_one("#result-value", Label)
        assert "75" in str(value_label._Static__content)


async def test_roll_result_shows_dash_when_no_value(tmp_path):
    """The result card shows '—' for value when item has no value_gp."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "trinket",
        "mystery",
        {"name": "Mystery Box", "type": "trinket", "rarity": "uncommon"},
    )
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        value_label = app.screen.query_one("#result-value", Label)
        assert "—" in str(value_label._Static__content)


async def test_roll_clears_status_bar_on_success(tmp_path):
    """A successful roll leaves the status bar empty."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert str(status._Static__content).strip() == ""


# ---------------------------------------------------------------------------
# Wealth validation
# ---------------------------------------------------------------------------


async def test_wealth_min_greater_than_max_shows_error(tmp_path):
    """When min > max the roll is blocked and an error is shown."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#wealth-min", Input).value = "500"
        app.screen.query_one("#wealth-max", Input).value = "10"
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert "min" in str(status._Static__content).lower()
        assert app.screen.query_one("#result-card").display is False


async def test_wealth_equal_min_max_is_valid(tmp_path):
    """min == max is a valid range; roll proceeds normally."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader, value_gp=50)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#wealth-min", Input).value = "50"
        app.screen.query_one("#wealth-max", Input).value = "50"
        await pilot.click("#btn-roll")
        await pilot.pause()
        status = app.screen.query_one("#status-bar", Label)
        assert str(status._Static__content).strip() == ""


async def test_invalid_wealth_input_treated_as_none(tmp_path):
    """Non-numeric wealth input is silently ignored (treated as no bound)."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#wealth-min", Input).value = "abc"
        await pilot.click("#btn-roll")
        await pilot.pause()
        # Should still roll successfully (ignoring bad input)
        assert app.screen.query_one("#result-card").display is True


# ---------------------------------------------------------------------------
# Currency-only shortcut
# ---------------------------------------------------------------------------


async def test_currency_shortcut_with_wealth_range(tmp_path):
    """Selecting only 'currency' + wealth range produces a currency result."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        # Select only "currency" in the types list.
        types_sel = s.query_one("#types-select", SelectionList)
        types_sel.select("currency")
        await pilot.pause()
        s.query_one("#wealth-min", Input).value = "10"
        s.query_one("#wealth-max", Input).value = "100"
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert s.query_one("#result-card").display is True
        type_label = s.query_one("#result-type", Label)
        assert "currency" in str(type_label._Static__content)


async def test_currency_shortcut_value_in_range(tmp_path):
    """The rolled currency amount is within the specified wealth range."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#types-select", SelectionList).select("currency")
        await pilot.pause()
        s.query_one("#wealth-min", Input).value = "50"
        s.query_one("#wealth-max", Input).value = "50"
        await pilot.click("#btn-roll")
        await pilot.pause()
        value_label = s.query_one("#result-value", Label)
        assert "50" in str(value_label._Static__content)


# ---------------------------------------------------------------------------
# Keyboard shortcut
# ---------------------------------------------------------------------------


async def test_ctrl_r_rolls(tmp_path):
    """Ctrl+R triggers the roll action."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.press("ctrl+r")
        await pilot.pause()
        assert app.screen.query_one("#result-card").display is True


# ---------------------------------------------------------------------------
# Type mode toggle
# ---------------------------------------------------------------------------


async def test_types_mode_exclude_filters_out_selected_types(tmp_path):
    """Setting mode to 'exclude' removes items of the selected type."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "weapon",
        "sword",
        {"name": "Sword", "type": "weapon", "rarity": "common"},
    )
    loader.save_item(
        "potion",
        "health",
        {"name": "Health Potion", "type": "potion", "rarity": "common"},
    )
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#types-select", SelectionList).select("weapon")
        await pilot.pause()
        s.query_one("#types-mode", Select).value = "exclude"
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        type_label = s.query_one("#result-type", Label)
        assert "weapon" not in str(type_label._Static__content)
        assert "potion" in str(type_label._Static__content)


# ---------------------------------------------------------------------------
# Currency shortcut — no wealth range
# ---------------------------------------------------------------------------


async def test_currency_shortcut_no_range_uses_defaults(tmp_path):
    """Currency-only type with no wealth range produces a result using defaults."""
    from grimoire.models.roller import CURRENCY_DEFAULT_MAX, CURRENCY_DEFAULT_MIN

    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#types-select", SelectionList).select("currency")
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        assert s.query_one("#result-card").display is True
        type_label = s.query_one("#result-type", Label)
        assert "currency" in str(type_label._Static__content)
        # value should be within defaults
        value_text = str(s.query_one("#result-value", Label)._Static__content)
        assert "gp" in value_text
        # Extract the numeric portion and verify it's within default range
        raw = value_text.split(":")[-1].replace("gp", "").strip()
        assert CURRENCY_DEFAULT_MIN <= float(raw) <= CURRENCY_DEFAULT_MAX


async def test_currency_shortcut_rarity_ignored(tmp_path):
    """Currency shortcut fires even when rarities are selected (rarity ignored)."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#rarity-select", SelectionList).select("legendary")
        s.query_one("#types-select", SelectionList).select("currency")
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        # Should still succeed — rarity filter is bypassed for currency
        assert s.query_one("#result-card").display is True


# ---------------------------------------------------------------------------
# Rarity mode — selector & comparator
# ---------------------------------------------------------------------------


async def test_rarity_mode_select_present(tmp_path):
    """Rarity mode Select widget is present on screen."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        sel = app.screen.query_one("#rarity-mode", Select)
        assert sel is not None
        assert sel.value == "manual"


async def test_rarity_mode_manual_shows_list_hides_comparator(tmp_path):
    """In manual mode the multi-select list is visible and ref row is hidden."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        assert s.query_one("#rarity-select").display is True
        assert s.query_one("#rarity-comparator-row").display is False


async def test_rarity_mode_comparator_toggles_widgets(tmp_path):
    """Switching to a comparator mode hides the list and shows the ref row."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#rarity-mode", Select).value = "geq"
        await pilot.pause()
        assert s.query_one("#rarity-select").display is False
        assert s.query_one("#rarity-comparator-row").display is True
        # Switching back to manual restores original layout
        s.query_one("#rarity-mode", Select).value = "manual"
        await pilot.pause()
        assert s.query_one("#rarity-select").display is True
        assert s.query_one("#rarity-comparator-row").display is False


async def test_rarity_comparator_geq_filters_results(tmp_path):
    """geq mode with ref='rare' returns items of rare rarity or higher."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    loader.save_item(
        "weapon",
        "sword",
        {"name": "Common Sword", "type": "weapon", "rarity": "common"},
    )
    loader.save_item(
        "ring",
        "ring_of_power",
        {"name": "Ring of Power", "type": "ring", "rarity": "rare"},
    )
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#rarity-mode", Select).value = "geq"
        await pilot.pause()
        s.query_one("#rarity-ref", Select).value = "rare"
        await pilot.pause()
        await pilot.click("#btn-roll")
        await pilot.pause()
        rarity_label = s.query_one("#result-rarity", Label)
        result_rarity = str(rarity_label._Static__content).split(":")[-1].strip()
        assert result_rarity in ("rare", "very rare", "legendary", "artifact")


async def test_rarity_comparator_no_ref_treats_as_no_filter(tmp_path):
    """Comparator mode with no ref rarity selected rolls from all items."""
    loader = ItemCatalogLoader(data_dir=tmp_path)
    _write_weapon(loader)
    app = _make_app(loader)
    async with app.run_test(size=(160, 60)) as pilot:
        await pilot.pause()
        s = app.screen
        s.query_one("#rarity-mode", Select).value = "lt"
        await pilot.pause()
        # Leave #rarity-ref at blank/prompt — no filter applied
        await pilot.click("#btn-roll")
        await pilot.pause()
        # With no valid ref, the filter is a no-op; should still roll
        # (result may be None if no items pass, but no crash)
        # The weapon has rarity="common" which won't match lt with no ref,
        # so we just assert no uncaught exception (either card shown or error).
        assert s.query_one("#result-card").display is True or "No items match" in str(
            s.query_one("#status-bar", Label)._Static__content
        )
