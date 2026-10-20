"""The sunset system: golden hour, dusk, and the end of a finished day. Pure, no IO."""

import re
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime, time, timedelta

from scrolly.domain.appearance import Phase
from scrolly.domain.day_budget import DEFAULT_SUNSET, sunset_at
from scrolly.domain.models import OPEN_STATES, Day, Trial

GOLDEN_LEAD = timedelta(hours=1)
FINISHED = "dusk"  # what `Day.dusk_override` holds once dusk is forced for the day


class SunsetError(ValueError):
    """A sunset time that cannot be read. The message is shown to the user."""


@dataclass(frozen=True)
class SunsetPrefs:
    """`invited` is true once the user has answered (a time, or "not now")."""

    enabled: bool = False
    invited: bool = False
    hour: int = DEFAULT_SUNSET.hour
    minute: int = DEFAULT_SUNSET.minute
    chime: bool = False

    @property
    def at(self) -> time:
        return time(self.hour, self.minute)


def parse_sunset_time(text: str) -> time:
    """`21`, `9:30` or `21:00`. Anything else is refused with a hint."""
    match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?", text.strip())
    hour, minute = (int(match[1]), int(match[2] or 0)) if match else (-1, -1)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise SunsetError("Use a time like 21:00")
    return time(hour, minute)


def budget_sunset(prefs: SunsetPrefs) -> time | None:
    """The sunset the Day Summary counts light against; none when the user said "not now".

    Until the user answers, the default hour is shown but nothing changes colour.
    """
    if not prefs.invited:
        return DEFAULT_SUNSET
    return prefs.at if prefs.enabled else None


def phase_at(now: datetime, prefs: SunsetPrefs, day: Day | None) -> Phase:
    """The palette phase: dusk when forced for the day, else by the clock around the sunset."""
    if day is not None and day.dusk_override == FINISHED:
        return Phase.DUSK
    if not prefs.enabled:
        return Phase.DAY
    sunset = sunset_at(now, prefs.at)
    if now >= sunset:
        return Phase.DUSK
    return Phase.GOLDEN if now >= sunset - GOLDEN_LEAD else Phase.DAY


def day_finished(day: Day | None, trials: Sequence[Trial]) -> bool:
    """The day began and no trial is left open (conquered, let go or postponed)."""
    if day is None or day.first_sealed_at is None:
        return False
    return not any(t.state in OPEN_STATES for t in trials)


def settle_finished(day: Day | None, trials: Sequence[Trial]) -> Day | None:
    """Finishing the day brings dusk for the rest of the logical day, even after a new trial."""
    if day is None or day.dusk_override == FINISHED or not day_finished(day, trials):
        return day
    return replace(day, dusk_override=FINISHED)
