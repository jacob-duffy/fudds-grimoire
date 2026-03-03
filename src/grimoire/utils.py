"""General-purpose utility helpers for Fudd's Grimoire."""

import re


def slugify(name: str) -> str:
    """Convert a display name to a snake_case item ID.

    Examples:
        >>> slugify("Iron Sword")
        'iron_sword'
        >>> slugify("+1 Longsword")
        '1_longsword'
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def num(text: str) -> int | float:
    """Parse *text* as a number.

    Returns an ``int`` when the value is a whole number (e.g. ``"5"`` → ``5``),
    otherwise a ``float`` (e.g. ``"5.5"`` → ``5.5``).
    Raises ``ValueError`` on non-numeric input.
    """
    value = float(text)
    return int(value) if value == int(value) else value
