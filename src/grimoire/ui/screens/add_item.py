"""Add New Item screen for Fudd's Grimoire."""

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Switch

from grimoire.loaders.items import TYPE_TO_SUBFORM, ItemCatalogLoader
from grimoire.loaders.tables import LootTableLoader
from grimoire.models.constants import SUBFORM_IDS
from grimoire.ui.constants import (
    ACTIVATION_OPTIONS,
    DAMAGE_TYPES,
    DENOMINATION_OPTIONS,
    DEX_BONUS_OPTIONS,
    ITEM_TYPES,
    MAGIC_BONUS_OPTIONS,
    RARITIES,
    WEAPON_PROPERTIES,
)
from grimoire.ui.utils import opts
from grimoire.ui.widgets import FormFieldRow
from grimoire.utils import num, slugify


class AddItemScreen(Screen):
    """Form screen for creating and saving a new item to a catalog YAML file.

    Sub-forms for weapon, armor, consumable, wondrous, and currency stats are
    shown or hidden automatically as the user changes the item type.  All
    changes are written to the appropriate ``.data/items/<category>.yml`` file
    on save.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+s", "save_item", "Save"),
    ]

    DEFAULT_CSS = """
    AddItemScreen {
        background: $surface;
    }

    #form-scroll {
        width: 100%;
        height: 1fr;
        padding: 1 2;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    #actions {
        height: auto;
        padding: 1 2;
        align-horizontal: right;
    }

    #status-bar {
        height: 1;
        padding: 0 2;
        color: $error;
    }

    #subform-weapon,
    #subform-armor,
    #subform-consumable,
    #subform-wondrous,
    #subform-currency {
        display: none;
        height: auto;
    }

    #row-attunement-req {
        display: none;
    }
    """

    def __init__(
        self,
        loader: ItemCatalogLoader | None = None,
        table_loader: LootTableLoader | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._loader = loader or ItemCatalogLoader()
        self._table_loader: LootTableLoader | None = table_loader
        # Maps Select value (str(path)) → Path, populated in on_mount.
        self._table_paths: dict[str, Path] = {}

    def compose(
        self,
    ) -> ComposeResult:  # noqa: PLR0915 (many yields is expected for a form)
        yield Header()
        yield Label("", id="status-bar")

        with VerticalScroll(id="form-scroll"):
            # ── Basic info (required) ────────────────────────────────────────
            yield Label("Basic Info", classes="section-title")
            with FormFieldRow("Item Type *"):
                yield Select(
                    opts(ITEM_TYPES),
                    prompt="Select type…",
                    id="field-type",
                    classes="field-input",
                )
            with FormFieldRow("Name *"):
                yield Input(
                    placeholder="e.g. Iron Sword",
                    id="field-name",
                    classes="field-input",
                )
            with FormFieldRow("Rarity *"):
                yield Select(
                    opts(RARITIES),
                    prompt="Select rarity…",
                    id="field-rarity",
                    classes="field-input",
                )
            with FormFieldRow("Link to Table"):
                yield Select(
                    [],
                    prompt="None — save to item catalog",
                    id="field-table",
                    classes="field-input",
                    disabled=True,
                )
            yield Label("General", classes="section-title")
            with FormFieldRow("Description"):
                yield Input(
                    placeholder="Flavour or mechanical text",
                    id="field-description",
                    classes="field-input",
                )
            with FormFieldRow("Value (GP)"):
                yield Input(
                    placeholder="e.g. 50",
                    id="field-value-gp",
                    classes="field-input",
                )
            with FormFieldRow("Weight (lb)"):
                yield Input(
                    placeholder="e.g. 3.0",
                    id="field-weight-lb",
                    classes="field-input",
                )
            with FormFieldRow("Attunement"):
                yield Switch(value=False, id="field-attunement")
            with FormFieldRow("  └ Requirements", id="row-attunement-req"):
                yield Input(
                    placeholder="e.g. by a spellcaster",
                    id="field-attunement-req",
                    classes="field-input",
                )
            with FormFieldRow("Magical"):
                yield Switch(value=False, id="field-magical")
            with FormFieldRow("Tags"):
                yield Input(
                    placeholder="Comma-separated, e.g. fire, damage",
                    id="field-tags",
                    classes="field-input",
                )
            with FormFieldRow("Source"):
                yield Input(
                    placeholder="e.g. PHB, DMG, homebrew",
                    id="field-source",
                    classes="field-input",
                )

            # ── Weapon sub-form ──────────────────────────────────────────────
            with Vertical(id="subform-weapon"):
                yield Label("Weapon Stats", classes="section-title")
                with FormFieldRow("Damage Dice"):
                    yield Input(
                        placeholder="e.g. 1d8",
                        id="field-weapon-dice",
                        classes="field-input",
                    )
                with FormFieldRow("Damage Type"):
                    yield Select(
                        opts(DAMAGE_TYPES),
                        prompt="Select damage type…",
                        id="field-weapon-dmg-type",
                        classes="field-input",
                    )
                with FormFieldRow("Properties"):
                    yield Input(
                        placeholder=(
                            "Comma-separated: " f"{', '.join(WEAPON_PROPERTIES[:4])}…"
                        ),
                        id="field-weapon-props",
                        classes="field-input",
                    )
                with FormFieldRow("Range Normal (ft)"):
                    yield Input(
                        placeholder="e.g. 80",
                        id="field-weapon-range-normal",
                        classes="field-input",
                    )
                with FormFieldRow("Range Long (ft)"):
                    yield Input(
                        placeholder="e.g. 320",
                        id="field-weapon-range-long",
                        classes="field-input",
                    )
                with FormFieldRow("Magic Bonus"):
                    yield Select(
                        MAGIC_BONUS_OPTIONS,
                        prompt="None",
                        id="field-weapon-magic-bonus",
                        classes="field-input",
                    )

            # ── Armor sub-form ───────────────────────────────────────────────
            with Vertical(id="subform-armor"):
                yield Label("Armor / Shield Stats", classes="section-title")
                with FormFieldRow("Base AC"):
                    yield Input(
                        placeholder="e.g. 14",
                        id="field-armor-base-ac",
                        classes="field-input",
                    )
                with FormFieldRow("Dex Bonus"):
                    yield Select(
                        opts(DEX_BONUS_OPTIONS),
                        prompt="Select…",
                        id="field-armor-dex-bonus",
                        classes="field-input",
                    )
                with FormFieldRow("Strength Req."):
                    yield Input(
                        placeholder="e.g. 15",
                        id="field-armor-str-req",
                        classes="field-input",
                    )
                with FormFieldRow("Stealth Disadv."):
                    yield Switch(
                        value=False,
                        id="field-armor-stealth",
                    )
                with FormFieldRow("Magic Bonus"):
                    yield Select(
                        MAGIC_BONUS_OPTIONS,
                        prompt="None",
                        id="field-armor-magic-bonus",
                        classes="field-input",
                    )

            # ── Consumable sub-form ──────────────────────────────────────────
            with Vertical(id="subform-consumable"):
                yield Label("Consumable Stats", classes="section-title")
                with FormFieldRow("Charges"):
                    yield Input(
                        placeholder="e.g. 1",
                        id="field-consumable-charges",
                        classes="field-input",
                    )
                with FormFieldRow("Spell"):
                    yield Input(
                        placeholder="e.g. Cure Wounds",
                        id="field-consumable-spell",
                        classes="field-input",
                    )
                with FormFieldRow("Spell Level"):
                    yield Input(
                        placeholder="0–9",
                        id="field-consumable-spell-level",
                        classes="field-input",
                    )
                with FormFieldRow("Healing Dice"):
                    yield Input(
                        placeholder="e.g. 2d4+2",
                        id="field-consumable-healing",
                        classes="field-input",
                    )

            # ── Wondrous sub-form ────────────────────────────────────────────
            with Vertical(id="subform-wondrous"):
                yield Label("Wondrous / Charged Item Stats", classes="section-title")
                with FormFieldRow("Max Charges"):
                    yield Input(
                        placeholder="e.g. 7",
                        id="field-wondrous-charges",
                        classes="field-input",
                    )
                with FormFieldRow("Recharge"):
                    yield Input(
                        placeholder="e.g. 1d6+1, dawn, never",
                        id="field-wondrous-recharge",
                        classes="field-input",
                    )
                with FormFieldRow("Activation"):
                    yield Select(
                        opts(ACTIVATION_OPTIONS),
                        prompt="Select…",
                        id="field-wondrous-activation",
                        classes="field-input",
                    )
                with FormFieldRow("Effects"):
                    yield Input(
                        placeholder="Comma-separated, e.g. Charm Person (1 charge)",
                        id="field-wondrous-effects",
                        classes="field-input",
                    )

            # ── Currency sub-form ────────────────────────────────────────────
            with Vertical(id="subform-currency"):
                yield Label("Currency", classes="section-title")
                with FormFieldRow("Denomination"):
                    yield Select(
                        opts(DENOMINATION_OPTIONS),
                        prompt="Select…",
                        id="field-currency-denom",
                        classes="field-input",
                    )

        with Horizontal(id="actions"):
            yield Button("Save  [Ctrl+S]", variant="primary", id="btn-save")
            yield Button("Cancel  [Esc]", variant="default", id="btn-cancel")

        yield Footer()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        """Hide sub-forms and the attunement requirements row initially.

        Also populates the loot-table dropdown with any ``.yml`` files found
        in the configured tables directory.
        """
        self.query_one("#row-attunement-req").display = False
        for sf in SUBFORM_IDS:
            self.query_one(f"#subform-{sf}").display = False

        table_select = self.query_one("#field-table", Select)
        if self._table_loader is None:
            table_select.tooltip = "No loot table loader configured"
            return
        tables = self._table_loader.list_tables()
        if tables:
            self._table_paths = {str(path): path for _, path in tables}
            table_select.set_options([(label, str(path)) for label, path in tables])
            table_select.disabled = False
        else:
            table_select.tooltip = "No loot tables found in .data/tables/"

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    @on(Select.Changed, "#field-type")
    def on_type_changed(self, event: Select.Changed) -> None:
        """Show the correct sub-form when the item type selection changes."""
        val = event.value
        if val is Select.BLANK:
            selected = None
        else:
            s = str(val)
            selected = None if (not s or s == "Select.NULL") else s
        active = TYPE_TO_SUBFORM.get(selected) if selected else None
        for sf in SUBFORM_IDS:
            self.query_one(f"#subform-{sf}").display = sf == active

    @on(Switch.Changed, "#field-attunement")
    def on_attunement_toggle(self, event: Switch.Changed) -> None:
        """Show/hide the attunement requirements field."""
        self.query_one("#row-attunement-req").display = event.value

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_pressed(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#btn-save")
    def on_save_pressed(self) -> None:
        self._do_save()

    def action_save_item(self) -> None:
        """Keyboard shortcut handler for Ctrl+S."""
        self._do_save()

    # ------------------------------------------------------------------
    # Form collection & persistence
    # ------------------------------------------------------------------

    def _inp(self, field_id: str) -> str:
        """Return the stripped value of an Input widget."""
        return self.query_one(f"#{field_id}", Input).value.strip()

    def _sel(self, field_id: str) -> str | None:
        """Return the selected value of a Select widget, or None if blank."""
        val = self.query_one(f"#{field_id}", Select).value
        if val is Select.BLANK:
            return None
        s = str(val)
        # Guard against the BLANK sentinel's string representation ('Select.NULL')
        # which can appear when the 'is' identity check fails across import paths.
        if not s or s == "Select.NULL":
            return None
        return s

    def _do_save(self) -> None:
        """Validate form, build item dict, and write to the catalog file."""
        status = self.query_one("#status-bar", Label)

        # -- required fields --------------------------------------------------
        type_val = self._sel("field-type")
        name_val = self._inp("field-name")
        rarity_val = self._sel("field-rarity")

        errors: list[str] = []
        if type_val is None:
            errors.append("Item Type is required.")
        if not name_val:
            errors.append("Name is required.")
        if rarity_val is None:
            errors.append("Rarity is required.")

        if errors:
            status.update(" | ".join(errors))
            return

        status.update("")

        item_type: str = type_val  # type: ignore[assignment]
        item_data: dict = {
            "name": name_val,
            "type": item_type,
            "rarity": rarity_val,
        }

        # -- common optional fields -------------------------------------------
        if desc := self._inp("field-description"):
            item_data["description"] = desc
        if vgp := self._inp("field-value-gp"):
            try:
                item_data["value_gp"] = num(vgp)
            except ValueError:
                pass
        if wlb := self._inp("field-weight-lb"):
            try:
                item_data["weight_lb"] = num(wlb)
            except ValueError:
                pass
        attunement = self.query_one("#field-attunement", Switch).value
        if attunement:
            item_data["attunement"] = True
            if att_req := self._inp("field-attunement-req"):
                item_data["attunement_requirements"] = att_req
        if self.query_one("#field-magical", Switch).value:
            item_data["magical"] = True
        if tags_raw := self._inp("field-tags"):
            item_data["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
        if source := self._inp("field-source"):
            item_data["source"] = source

        # -- type-specific sub-form -------------------------------------------
        subform = TYPE_TO_SUBFORM.get(item_type)

        if subform == "weapon":
            if data := self._collect_weapon():
                item_data["weapon"] = data
        elif subform == "armor":
            if data := self._collect_armor():
                item_data["armor"] = data
        elif subform == "consumable":
            if data := self._collect_consumable():
                item_data["consumable"] = data
        elif subform == "wondrous":
            if data := self._collect_wondrous():
                item_data["wondrous"] = data
        elif subform == "currency":
            if denom := self._sel("field-currency-denom"):
                item_data["currency"] = {"denomination": denom}

        # -- persist ----------------------------------------------------------
        item_id = slugify(name_val)
        table_path_str = self._sel("field-table")
        table_path = self._table_paths.get(table_path_str) if table_path_str else None

        try:
            if table_path is not None:
                self._table_loader.append_inline_item(table_path, item_data)
                self.app.pop_screen()
                self.app.notify(
                    f'Added "{name_val}" → {table_path.name} (inline entry)',
                    title="Item Saved",
                )
            else:
                saved_path = self._loader.save_item(item_type, item_id, item_data)
                self.app.pop_screen()
                self.app.notify(
                    f'Saved "{name_val}" → {saved_path.name}',
                    title="Item Saved",
                )
        except Exception as exc:  # noqa: BLE001
            status.update(f"Error saving: {exc}")

    # ------------------------------------------------------------------
    # Sub-form collectors
    # ------------------------------------------------------------------

    def _collect_weapon(self) -> dict:
        """Read weapon sub-form fields and return a populated dict (may be empty)."""
        weapon: dict = {}
        dice = self._inp("field-weapon-dice")
        dmg_type = self._sel("field-weapon-dmg-type")
        if dice and dmg_type:
            weapon["damage"] = {"dice": dice, "type": dmg_type}
        if props_raw := self._inp("field-weapon-props"):
            weapon["properties"] = [
                p.strip() for p in props_raw.split(",") if p.strip()
            ]
        if rn := self._inp("field-weapon-range-normal"):
            try:
                weapon["range_normal_ft"] = int(rn)
            except ValueError:
                pass
        if rl := self._inp("field-weapon-range-long"):
            try:
                weapon["range_long_ft"] = int(rl)
            except ValueError:
                pass
        if mb := self._sel("field-weapon-magic-bonus"):
            if mb:
                weapon["magic_bonus"] = int(mb)
        return weapon

    def _collect_armor(self) -> dict:
        """Read armor sub-form fields and return a populated dict (may be empty)."""
        armor: dict = {}
        if bac := self._inp("field-armor-base-ac"):
            try:
                armor["base_ac"] = int(bac)
            except ValueError:
                pass
        if db := self._sel("field-armor-dex-bonus"):
            armor["dex_bonus"] = db
        if sr := self._inp("field-armor-str-req"):
            try:
                armor["strength_requirement"] = int(sr)
            except ValueError:
                pass
        if self.query_one("#field-armor-stealth", Switch).value:
            armor["stealth_disadvantage"] = True
        if mb := self._sel("field-armor-magic-bonus"):
            if mb:
                armor["magic_bonus"] = int(mb)
        return armor

    def _collect_consumable(self) -> dict:
        """Read consumable subform fields and return a populated dict (may be empty)."""
        consumable: dict = {}
        if ch := self._inp("field-consumable-charges"):
            try:
                consumable["charges"] = int(ch)
            except ValueError:
                pass
        if sp := self._inp("field-consumable-spell"):
            consumable["spell"] = sp
        if sl := self._inp("field-consumable-spell-level"):
            try:
                consumable["spell_level"] = int(sl)
            except ValueError:
                pass
        if hd := self._inp("field-consumable-healing"):
            consumable["healing_dice"] = hd
        return consumable

    def _collect_wondrous(self) -> dict:
        """Read wondrous sub-form fields and return a populated dict (may be empty)."""
        wondrous: dict = {}
        if ch := self._inp("field-wondrous-charges"):
            try:
                wondrous["charges"] = int(ch)
            except ValueError:
                pass
        if rc := self._inp("field-wondrous-recharge"):
            wondrous["recharge"] = rc
        if act := self._sel("field-wondrous-activation"):
            wondrous["activation"] = act
        if eff_raw := self._inp("field-wondrous-effects"):
            wondrous["effects"] = [e.strip() for e in eff_raw.split(",") if e.strip()]
        return wondrous
