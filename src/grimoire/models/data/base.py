"""Base item model — common header fields shared by every item type."""

from typing import Optional

from pydantic import BaseModel, Field

from grimoire.models.constants import ItemType, Rarity


class BaseItem(BaseModel):
    """Header fields present on every catalog item.

    All fields use their YAML key names so that
    ``BaseItem.model_validate(raw_dict)`` works directly against catalog data.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    type: ItemType
    rarity: Rarity
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    value_gp: Optional[float] = None
    requires_attunement: bool = False
    weight: Optional[float] = None

    model_config = {"populate_by_name": True}
