"""Roll Table screen for Fudd's Grimoire."""

import random
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Select,
)

from grimoire.loaders.items import ItemCatalogLoader
from grimoire.loaders.tables import LootTableLoader
from grimoire.models.roller import load_all_items
from grimoire.ui.widgets import ItemCard


class RollTableScreen(Screen):
    """Screen for rolling on a chosen loot table.

    Layout
    ------
    Three-column layout:

    * **Control pane** (left) — table selector and Roll button.
    * **Items list** (middle) — all entries in the selected table as a
      clickable list.  Selecting an entry updates the detail card.
    * **Item card** (right) — shows the full details of whichever entry is
      currently highlighted (via click *or* the Roll button's random pick).

    Users can either:

    * Click any entry in the list to inspect it, or
    * Press **Roll** (or Ctrl+R) to have one entry selected at random
      (respecting each entry's ``weight``) and its details displayed.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+r", "roll", "Roll"),
    ]

    DEFAULT_CSS = """
    RollTableScreen {
        background: $surface;
    }

    #layout {
        width: 100%;
        height: 1fr;
    }

    /* ── left pane ─────────────────────────────────────────────────── */
    #control-pane {
        width: 32;
        height: 100%;
        border-right: solid $primary;
        padding: 0 1;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    #table-select {
        width: 100%;
        margin-bottom: 1;
    }

    #btn-roll {
        margin-top: 1;
        width: 100%;
    }

    #hint-label {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
        width: 100%;
    }

    /* ── middle pane: items list ────────────────────────────────────── */
    #list-pane {
        width: 36;
        height: 100%;
        border-right: solid $primary;
        padding: 0 1;
    }

    #list-placeholder {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
    }

    #items-list {
        display: none;
        width: 100%;
        height: 1fr;
    }

    /* ── right pane: item card ──────────────────────────────────────── */
    #card-pane {
        width: 1fr;
        height: 100%;
        padding: 1 2;
    }

    #table-info {
        color: $text-muted;
        width: 100%;
        margin-bottom: 1;
    }

    #status-bar {
        height: 1;
        padding: 0 1;
        color: $error;
    }
    """

    def __init__(
        self,
        table_loader: LootTableLoader | None = None,
        catalog_loader: ItemCatalogLoader | None = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._table_loader = table_loader or LootTableLoader()
        self._catalog_loader = catalog_loader or ItemCatalogLoader()
        self._tables: list[tuple[str, Path]] = []
        # Resolved entries for the currently loaded table.
        # Each entry is the fully-resolved item dict, augmented with a
        # ``_weight`` key for weighted random selection.
        self._resolved_entries: list[dict] = []
        # Raw table dict for the currently selected table.
        self._current_table: dict | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        """Populate the table selector after the DOM is ready."""
        self._tables = self._table_loader.list_tables()
        selector = self.query_one("#table-select", Select)

        if self._tables:
            options = [(label, str(path)) for label, path in self._tables]
            selector.set_options(options)
        else:
            selector.set_options([("No tables found", "_none")])
            self.query_one("#btn-roll", Button).disabled = True
            self.query_one("#status-bar", Label).update(
                "No tables found. Create a table file under .data/tables/ first."
            )

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("", id="status-bar")

        with Horizontal(id="layout"):
            # ── Left: controls ────────────────────────────────────────
            with VerticalScroll(id="control-pane"):
                yield Label("Table", classes="section-title")
                yield Select(
                    [],
                    prompt="Select a table…",
                    id="table-select",
                    allow_blank=True,
                )
                yield Button("Roll", id="btn-roll", variant="primary")
                yield Label(
                    "Click an item or press Roll (Ctrl+R)",
                    id="hint-label",
                )

            # ── Middle: item list ─────────────────────────────────────
            with Vertical(id="list-pane"):
                yield Label("Items", classes="section-title")
                yield Label(
                    "Select a table to view its entries",
                    id="list-placeholder",
                )
                yield ListView(id="items-list")

            # ── Right: item card ──────────────────────────────────────
            with Vertical(id="card-pane"):
                yield Label("", id="table-info")
                yield ItemCard()

        yield Footer()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    @on(Select.Changed, "#table-select")
    def on_table_changed(self, event: Select.Changed) -> None:
        """Load the table entries into the list when the user picks a table."""
        self.query_one("#status-bar", Label).update("")
        self._clear_card()

        selected_value = event.value
        if selected_value is Select.BLANK or selected_value == "_none":
            self._clear_list()
            return

        path = Path(str(selected_value))
        table = self._table_loader.load(path)
        self._current_table = table
        self._load_entries(table)

        # Show the table description as soon as the table is selected.
        table_id = table.get("id", path.stem)
        desc = table.get("description", "")
        info_parts = [f"Table: {table_id}"]
        if desc:
            info_parts.append(desc)
        self.query_one("#table-info", Label).update(" — ".join(info_parts))

    @on(ListView.Highlighted, "#items-list")
    def on_item_highlighted(self, event: ListView.Highlighted) -> None:
        """Show whichever list entry is highlighted in the detail card."""
        if event.item is None:
            return
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self._resolved_entries):
            self._show_in_card(self._resolved_entries[idx])

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_roll(self) -> None:
        """Keyboard shortcut: trigger a roll."""
        self._do_roll()

    @on(Button.Pressed, "#btn-roll")
    def on_roll_pressed(self) -> None:
        self._do_roll()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_entries(self, table: dict) -> None:
        """Resolve every entry in *table* and populate the items list.

        ``reference:`` entries are expanded recursively: the referenced table
        is loaded by its ``id``, and its entries are inlined into this list.
        Cycles are detected via a visited-set and fall back to a
        ``[Table: <id>]`` stub when encountered.  When a referenced table
        cannot be found the same stub is used.

        Each resolved item dict is stored in ``self._resolved_entries`` with
        an extra ``_weight`` key (parent_weight × entry_weight) so weighted
        random selection works correctly across the flat list.
        """
        item_index: dict[str, dict] = {
            item["_id"]: item
            for item in load_all_items(self._catalog_loader)
            if "_id" in item
        }

        self._resolved_entries = []
        self._expand_entries(table.get("entries", []), item_index, frozenset())

        list_widget = self.query_one("#items-list", ListView)
        list_widget.clear()
        for item in self._resolved_entries:
            name = item.get("name") or item.get("_id") or "Unknown"
            list_widget.append(ListItem(Label(name)))

        has_entries = bool(self._resolved_entries)
        self.query_one("#list-placeholder", Label).display = not has_entries
        list_widget.display = has_entries

    def _expand_entries(
        self,
        entries: list,
        item_index: dict,
        visited: frozenset[str],
        parent_weight: int = 1,
    ) -> None:
        """Recursively resolve *entries* into ``self._resolved_entries``.

        Parameters
        ----------
        entries:
            Raw entry dicts from a table's ``entries`` list.
        item_index:
            Pre-built ``id → item`` map from the item catalog.
        visited:
            Set of table IDs already seen on the current resolution path.
            Used to detect and break reference cycles.
        parent_weight:
            Cumulative weight inherited from ancestor ``reference`` entries.
            Each entry's effective weight is ``entry_weight × parent_weight``.
        """
        for entry in entries:
            weight = max(int(entry.get("weight", 1)), 1) * parent_weight

            if "item" in entry:
                item = dict(entry["item"])
                item.setdefault("_id", item.get("name", "inline_item"))
                item["_weight"] = weight
                self._resolved_entries.append(item)

            elif "item_ref" in entry:
                item_id = str(entry["item_ref"])
                found = item_index.get(item_id)
                if found is not None:
                    item = dict(found)
                    item["_weight"] = weight
                    self._resolved_entries.append(item)
                else:
                    self._resolved_entries.append(
                        {"_id": item_id, "name": item_id, "_weight": weight}
                    )

            elif "reference" in entry:
                ref_id = str(entry["reference"])
                if ref_id not in visited:
                    sub_table = self._table_loader.find_by_id(ref_id)
                    if sub_table is not None:
                        self._expand_entries(
                            sub_table.get("entries", []),
                            item_index,
                            visited | {ref_id},
                            weight,
                        )
                        continue
                # Sub-table not found or cycle detected — show stub.
                self._resolved_entries.append(
                    {
                        "_id": f"_ref:{ref_id}",
                        "name": f"[Table: {ref_id}]",
                        "_weight": weight,
                    }
                )

    def _do_roll(self) -> None:
        """Perform a weighted random pick and update the highlighted entry."""
        status = self.query_one("#status-bar", Label)
        status.update("")

        selector = self.query_one("#table-select", Select)
        selected_value = selector.value

        if selected_value is Select.BLANK or selected_value == "_none":
            status.update("Please select a table first.")
            return

        if not self._resolved_entries:
            status.update("The table has no entries or produced no results.")
            return

        weights = [item.get("_weight", 1) for item in self._resolved_entries]
        chosen = random.choices(self._resolved_entries, weights=weights, k=1)[0]
        idx = self._resolved_entries.index(chosen)

        # Highlight the chosen entry in the list.
        items_list = self.query_one("#items-list", ListView)
        items_list.index = idx

        self._show_in_card(chosen)

    def _show_in_card(self, item: dict) -> None:
        """Populate the detail card with the given item's fields."""
        self.query_one("#hint-label", Label).display = False
        self.query_one(ItemCard).populate(item)

    def _clear_card(self) -> None:
        """Reset the card panel to its initial placeholder state."""
        self.query_one("#hint-label", Label).display = True
        self.query_one(ItemCard).clear()
        self.query_one("#table-info", Label).update("")

    def _clear_list(self) -> None:
        """Clear the items list and reset resolved entry state."""
        self._resolved_entries = []
        self._current_table = None
        list_widget = self.query_one("#items-list", ListView)
        list_widget.clear()
        list_widget.display = False
        self.query_one("#list-placeholder", Label).display = True
