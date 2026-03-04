"""Item sub-form data collectors for Fudd's Grimoire.

Each function accepts the raw string (or optional-string) values read
directly from the form widgets and returns a populated ``dict`` ready to
be embedded under the relevant key in an item payload.  The functions are
intentionally decoupled from any Textual widget — they receive plain Python
values so they can be called from screens, tests, or non-UI code alike.

All collectors return an empty dict when no meaningful data is provided.
"""


def collect_weapon(
    dice: str,
    dmg_type: str | None,
    props_raw: str,
    range_normal: str,
    range_long: str,
    magic_bonus: str | None,
) -> dict:
    """Build the ``weapon`` sub-dict from raw form values.

    Parameters
    ----------
    dice:
        Damage dice string, e.g. ``"1d8"``.
    dmg_type:
        Selected damage type string, or ``None`` if blank.
    props_raw:
        Raw comma-separated properties string, e.g. ``"finesse, light"``.
    range_normal:
        Normal range in feet as a string, e.g. ``"80"``.
    range_long:
        Long range in feet as a string, e.g. ``"320"``.
    magic_bonus:
        Selected magic bonus string (``"+1"``, ``"+2"``, etc.), or ``None``.
    """
    weapon: dict = {}
    if dice and dmg_type:
        weapon["damage"] = {"dice": dice, "type": dmg_type}
    if props_raw:
        weapon["properties"] = [p.strip() for p in props_raw.split(",") if p.strip()]
    if range_normal:
        try:
            weapon["range_normal_ft"] = int(range_normal)
        except ValueError:
            pass
    if range_long:
        try:
            weapon["range_long_ft"] = int(range_long)
        except ValueError:
            pass
    if magic_bonus:
        try:
            weapon["magic_bonus"] = int(magic_bonus)
        except ValueError:
            pass
    return weapon


def collect_armor(
    base_ac: str,
    dex_bonus: str | None,
    str_req: str,
    stealth_disadv: bool,
    magic_bonus: str | None,
) -> dict:
    """Build the ``armor`` sub-dict from raw form values.

    Parameters
    ----------
    base_ac:
        Base AC value as a string, e.g. ``"14"``.
    dex_bonus:
        Selected dex bonus option string, or ``None`` if blank.
    str_req:
        Strength requirement as a string, e.g. ``"15"``.
    stealth_disadv:
        Whether the armor imposes stealth disadvantage.
    magic_bonus:
        Selected magic bonus string, or ``None``.
    """
    armor: dict = {}
    if base_ac:
        try:
            armor["base_ac"] = int(base_ac)
        except ValueError:
            pass
    if dex_bonus:
        armor["dex_bonus"] = dex_bonus
    if str_req:
        try:
            armor["strength_requirement"] = int(str_req)
        except ValueError:
            pass
    if stealth_disadv:
        armor["stealth_disadvantage"] = True
    if magic_bonus:
        try:
            armor["magic_bonus"] = int(magic_bonus)
        except ValueError:
            pass
    return armor


def collect_consumable(
    charges: str,
    spell: str,
    spell_level: str,
    healing_dice: str,
) -> dict:
    """Build the ``consumable`` sub-dict from raw form values.

    Parameters
    ----------
    charges:
        Number of charges as a string, e.g. ``"1"``.
    spell:
        Linked spell name, e.g. ``"Cure Wounds"``.
    spell_level:
        Spell level as a string, e.g. ``"2"``.
    healing_dice:
        Healing dice expression, e.g. ``"2d4+2"``.
    """
    consumable: dict = {}
    if charges:
        try:
            consumable["charges"] = int(charges)
        except ValueError:
            pass
    if spell:
        consumable["spell"] = spell
    if spell_level:
        try:
            consumable["spell_level"] = int(spell_level)
        except ValueError:
            pass
    if healing_dice:
        consumable["healing_dice"] = healing_dice
    return consumable


def collect_wondrous(
    charges: str,
    recharge: str,
    activation: str | None,
    effects_raw: str,
) -> dict:
    """Build the ``wondrous`` sub-dict from raw form values.

    Parameters
    ----------
    charges:
        Maximum charges as a string, e.g. ``"7"``.
    recharge:
        Recharge condition string, e.g. ``"1d6+1, dawn"``.
    activation:
        Selected activation type string, or ``None`` if blank.
    effects_raw:
        Raw comma-separated effects string.
    """
    wondrous: dict = {}
    if charges:
        try:
            wondrous["charges"] = int(charges)
        except ValueError:
            pass
    if recharge:
        wondrous["recharge"] = recharge
    if activation:
        wondrous["activation"] = activation
    if effects_raw:
        wondrous["effects"] = [e.strip() for e in effects_raw.split(",") if e.strip()]
    return wondrous
