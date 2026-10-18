"""Small builders so tests state only what they care about."""

from datetime import date
from typing import Any

from scrolly.domain.models import HorizonItem, Trial, TrialState

DAY = date(2026, 10, 18)


def make_trial(title: str = "Trial", **fields: Any) -> Trial:
    fields.setdefault("id", f"trial-{title}")
    fields.setdefault("logical_day", DAY)
    fields.setdefault("state", TrialState.REMAINING)
    return Trial(title=title, **fields)


def make_item(title: str = "Item", **fields: Any) -> HorizonItem:
    fields.setdefault("id", f"item-{title}")
    return HorizonItem(title=title, **fields)
