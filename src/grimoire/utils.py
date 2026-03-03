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
