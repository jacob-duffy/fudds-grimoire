"""FormFieldRow widget for Fudd's Grimoire."""

from textual.containers import Horizontal
from textual.widgets import Label


class FormFieldRow(Horizontal):
    """A labelled form row with a flexible right-hand content area.

    Composes a fixed-width label on the left; whatever widgets are passed
    as children (via the compose context-manager DSL) fill the remaining
    width on the right.  Any child with ``classes="field-input"`` stretches
    to ``1fr``; children without it use their natural width.

    This means a single ``Input`` can fill the full right column, a nested
    ``Horizontal`` can hold multiple denomination inputs side-by-side, and a
    ``Switch`` sits neatly at its natural size rather than stretching to fill
    the row.

    Usage::

        # Stretching input
        with FormFieldRow("Name *"):
            yield Input(placeholder="…", id="field-name", classes="field-input")

        # Switch at natural width — no field-input class
        with FormFieldRow("Attunement"):
            yield Switch(value=False, id="field-attunement")

        # Multiple inputs sharing the row
        with FormFieldRow("Coin"):
            with Horizontal():
                yield Input(placeholder="GP", id="gp", classes="field-input")
                yield Input(placeholder="SP", id="sp", classes="field-input")
    """

    DEFAULT_CSS = """
    FormFieldRow {
        height: auto;
        margin-bottom: 1;
    }

    FormFieldRow > .field-label {
        width: 24;
        padding-top: 1;
    }

    FormFieldRow .field-input {
        width: 1fr;
    }
    """

    def __init__(self, label: str, *children, **kwargs) -> None:
        super().__init__(*children, **kwargs)
        self._label_text = label

    def on_mount(self) -> None:
        # Insert the label at index 0 so it always precedes the field widget(s),
        # regardless of when Textual mounts __init__ children relative to compose.
        self.mount(Label(self._label_text, classes="field-label"), before=0)
