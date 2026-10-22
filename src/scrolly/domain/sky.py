"""Where the sun or the moon stands, for the arc in Seclusion's top bar. Pure, no IO.

The sun crosses from the logical morning (06:00) to the user's sunset (the default hour if they keep
none); after it the moon crosses to the 04:00 that ends the logical day. The arc only shows where;
nothing here says how much of the day is left to work.
"""

from dataclasses import dataclass
from datetime import datetime, time
from enum import StrEnum

from scrolly.domain.day_budget import DEFAULT_SUNSET, sunset_at
from scrolly.domain.logical_day import logical_day, logical_day_end
from scrolly.domain.sunset import SunsetPrefs

MORNING = time(6, 0)


class Body(StrEnum):
    SUN = "sun"
    MOON = "moon"


@dataclass(frozen=True)
class Sky:
    body: Body
    progress: float  # 0 at the start of its crossing, 1 at the end


def _share(now: datetime, start: datetime, end: datetime) -> float:
    span = (end - start).total_seconds()
    return 0.0 if span <= 0 else min(1.0, max(0.0, (now - start).total_seconds() / span))


def sky_at(now: datetime, prefs: SunsetPrefs) -> Sky:
    day = logical_day(now)
    sunset = sunset_at(now, prefs.at if prefs.enabled else DEFAULT_SUNSET)
    if now < sunset:
        morning = datetime.combine(day, MORNING, tzinfo=now.tzinfo)
        return Sky(Body.SUN, _share(now, morning, sunset))
    return Sky(Body.MOON, _share(now, sunset, logical_day_end(day, like=now)))
