"""ItemCard widget for Fudd's Grimoire."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label


class ItemCard(Vertical):
    """A bordered card that displays the key fields of a resolved item dict.

    The card is hidden by default.  Call :meth:`update` to populate it and
    make it visible, or :meth:`clear` to hide it again.

    Because each label is queried via ``self.query_one`` (scoped to this
    widget's subtree), multiple ``ItemCard`` instances can safely coexist on
    the same screen without ID collisions.
    """

    DEFAULT_CSS = """
    ItemCard {
        display: none;
        height: auto;
        border: solid $primary;
        padding: 1 2;
        margin-top: 1;
        width: 100%;
    }

    ItemCard > .card-name {
        text-style: bold;
        color: $accent;
        width: 100%;
        margin-bottom: 1;
    }

    ItemCard > .card-field {
        width: 100%;
        margin-bottom: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("", classes="card-name")
        yield Label("", classes="card-type card-field")
        yield Label("", classes="card-rarity card-field")
        yield Label("", classes="card-value card-field")
        yield Label("", classes="card-desc card-field")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def populate(self, item: dict) -> None:
        """Populate all card fields from *item* and make the card visible.

        Parameters
        ----------
        item:
            A resolved item dict.  Expected keys: ``name`` / ``_id``,
            ``type``, ``rarity``, ``value_gp``, ``description``.
            Missing keys render as ``—``.
        """
        name = item.get("name") or item.get("_id") or "Unknown Item"
        self.query_one(".card-name", Label).update(name)
        self.query_one(".card-type", Label).update(f"Type:   {item.get('type', '—')}")
        self.query_one(".card-rarity", Label).update(
            f"Rarity: {item.get('rarity', '—')}"
        )

        value = item.get("value_gp")
        value_text = f"{value} gp" if value is not None else "—"
        self.query_one(".card-value", Label).update(f"Value:  {value_text}")

        desc = item.get("description", "")
        desc_label = self.query_one(".card-desc", Label)
        if desc:
            desc_label.update(f"\n{desc}")
            desc_label.display = True
        else:
            desc_label.display = False

        self.display = True

    def clear(self) -> None:
        """Hide the card without resetting its content."""
        self.display = False
