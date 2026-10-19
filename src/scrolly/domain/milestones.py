"""The milestone shown after the day's first seal: the Heavenly Cycles count and a quote. Pure."""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Quote:
    text: str
    attribution: str | None = None
    # A placeholder written for this app. Real, sourced quotes replace them in step 10.
    stand_in: bool = False


@dataclass(frozen=True)
class MilestoneRow:
    """A day with its own entry. No quote means the day takes the usual rotation."""

    day: int
    quote: Quote | None = None
    banner: str | None = None


@dataclass(frozen=True)
class Milestone:
    cycles: int
    quote: Quote
    banner: str | None


def milestone_for(cycles: int, rows: Sequence[MilestoneRow], quotes: Sequence[Quote]) -> Milestone:
    """What to show after sealing the `cycles`-th day. The same day always gets the same quote."""
    row = next((r for r in rows if r.day == cycles), None)
    quote = row.quote if row is not None and row.quote is not None else quotes[cycles % len(quotes)]
    return Milestone(cycles=cycles, quote=quote, banner=row.banner if row is not None else None)
