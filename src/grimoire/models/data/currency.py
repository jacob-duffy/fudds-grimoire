"""Currency item model."""

from typing import Optional

from grimoire.models.constants import Denomination
from grimoire.models.data.base import BaseItem


class CurrencyItem(BaseItem):
    """A currency catalog entry."""

    denomination: Optional[Denomination] = None
    amount: Optional[float] = None
