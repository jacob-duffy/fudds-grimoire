"""Roll Item screen for Fudd's Grimoire."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Select,
    SelectionList,
)

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.models.roller import roll_item
from grimoire.ui.constants import RARITY_MODE_OPTIONS, TYPE_MODE_OPTIONS
from grimoire.ui.utils import (
    rarity_comparator_options,
    rarity_selections,
    type_selections,
)
from grimoire.ui.widgets import ItemCard


class RollItemScreen(Screen):
    """Screen for rolling a random item from the catalog with optional filters.

    Filters act as constraints; leaving all selections empty means "any".

    Rarity filter
        Select one or more rarities.  Items of other rarities are excluded.
        Empty selection = all rarities allowed.

    Type filter
        Select one or more item types.  The mode toggle controls whether the
        list is *included* (only matching types) or *excluded* (all types
        except those selected).

    Wealth range
        Set optional min/max GP values.  Items outside the range are excluded.
        Items with no ``value_gp`` field always pass.

    Currency-only shortcut
        When the type filter is set to *include* exactly ``currency`` and a
        wealth range is provided, a random GP amount within the range is
        returned without consulting the catalog.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+r", "roll", "Roll"),
    ]

    DEFAULT_CSS = """
    RollItemScreen {
        background: $surface;
    }

    #layout {
        width: 100%;
        height: 1fr;
    }

    #filters-pane {
        width: 40;
        height: 100%;
        border-right: solid $primary;
        padding: 0 1;
    }

    #result-pane {
        width: 1fr;
        height: 100%;
        padding: 1 2;
        align-vertical: top;
    }

    .filter-section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    .filter-list {
        height: auto;
        max-height: 10;
        margin-bottom: 1;
        border: solid $primary-darken-2;
    }

    #rarity-mode-row {
        height: auto;
        margin-bottom: 0;
        align-vertical: middle;
    }

    #rarity-mode {
        width: 18;
        margin-left: 1;
    }

    #rarity-comparator-row {
        display: none;
        height: auto;
        margin-bottom: 1;
    }

    #rarity-ref {
        width: 1fr;
    }

    .wealth-row {
        height: auto;
        margin-bottom: 1;
    }

    .wealth-label {
        width: 6;
        padding-top: 1;
    }

    .wealth-input {
        width: 1fr;
    }

    #types-header {
        height: auto;
        margin-top: 0;
        margin-bottom: 0;
        align-vertical: middle;
    }

    #types-mode {
        width: 14;
        margin-left: 1;
    }

    #btn-roll {
        margin-top: 1;
        width: 100%;
    }

    #status-bar {
        height: 1;
        padding: 0 1;
        color: $error;
    }

    #result-placeholder {
        color: $text-muted;
        text-style: italic;
        margin-top: 2;
    }
    """

    def __init__(
        self,
        loader: ItemCatalogLoader | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._loader = loader or ItemCatalogLoader()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("", id="status-bar")

        with Horizontal(id="layout"):
            # ── Left: filter pane ──────────────────────────────────────────
            with VerticalScroll(id="filters-pane"):
                with Horizontal(id="rarity-mode-row"):
                    yield Label("Rarity", classes="filter-section-title")
                    yield Select(
                        RARITY_MODE_OPTIONS,
                        value="manual",
                        id="rarity-mode",
                        allow_blank=False,
                    )
                yield SelectionList[str](
                    *rarity_selections(),
                    id="rarity-select",
                    classes="filter-list",
                )
                with Horizontal(id="rarity-comparator-row"):
                    yield Select(
                        rarity_comparator_options(),
                        prompt="Select reference rarity…",
                        id="rarity-ref",
                    )

                with Horizontal(id="types-header"):
                    yield Label("Item Types", classes="filter-section-title")
                    yield Select(
                        TYPE_MODE_OPTIONS,
                        value="include",
                        id="types-mode",
                        allow_blank=False,
                    )
                yield SelectionList[str](
                    *type_selections(),
                    id="types-select",
                    classes="filter-list",
                )

                yield Label("Wealth Range (gp)", classes="filter-section-title")
                with Horizontal(classes="wealth-row"):
                    yield Label("Min:", classes="wealth-label")
                    yield Input(
                        placeholder="e.g. 10",
                        id="wealth-min",
                        classes="wealth-input",
                    )
                with Horizontal(classes="wealth-row"):
                    yield Label("Max:", classes="wealth-label")
                    yield Input(
                        placeholder="e.g. 500",
                        id="wealth-max",
                        classes="wealth-input",
                    )

                yield Button("Roll", id="btn-roll", variant="primary")

            # ── Right: result pane ─────────────────────────────────────────
            with Vertical(id="result-pane"):
                yield Label(
                    "Set filters and press Roll (Ctrl+R)",
                    id="result-placeholder",
                )
                yield ItemCard()

        yield Footer()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_roll(self) -> None:
        """Keyboard binding: trigger a roll."""
        self._do_roll()

    @on(Button.Pressed, "#btn-roll")
    def on_roll_pressed(self) -> None:
        self._do_roll()

    @on(Select.Changed, "#rarity-mode")
    def on_rarity_mode_changed(self, event: Select.Changed) -> None:
        """Toggle between manual multi-select and comparator single-select."""
        is_manual = event.value == "manual"
        self.query_one("#rarity-select").display = is_manual
        self.query_one("#rarity-comparator-row").display = not is_manual

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_wealth(self, widget_id: str) -> float | None:
        """Return the float value of a wealth input, or None if empty/invalid."""
        raw = self.query_one(f"#{widget_id}", Input).value.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _do_roll(self) -> None:
        """Collect filter values, call the roller, and display the result."""
        status = self.query_one("#status-bar", Label)
        status.update("")

        rarity_mode = str(self.query_one("#rarity-mode", Select).value or "manual")
        if rarity_mode == "manual":
            rarities = list(self.query_one("#rarity-select", SelectionList).selected)
            rarity_ref = None
        else:
            rarities = None
            ref_val = self.query_one("#rarity-ref", Select).value
            rarity_ref = str(ref_val) if ref_val else None

        types = list(self.query_one("#types-select", SelectionList).selected)
        types_mode = str(self.query_one("#types-mode", Select).value or "include")
        wealth_min = self._parse_wealth("wealth-min")
        wealth_max = self._parse_wealth("wealth-max")

        # Validate wealth range
        if wealth_min is not None and wealth_max is not None:
            if wealth_min > wealth_max:
                status.update("Wealth min must be ≤ max.")
                return

        result = roll_item(
            self._loader,
            rarities=rarities or None,
            rarity_mode=rarity_mode,
            rarity_ref=rarity_ref,
            types=types or None,
            types_mode=types_mode,
            wealth_min=wealth_min,
            wealth_max=wealth_max,
        )

        if result is None:
            status.update("No items match the current filters.")
            self.query_one(ItemCard).clear()
            self.query_one("#result-placeholder").display = True
            return

        self._display_result(result)

    def _display_result(self, item: dict) -> None:
        """Populate the result card with *item* data and make it visible."""
        self.query_one("#result-placeholder", Label).display = False
        self.query_one(ItemCard).populate(item)
