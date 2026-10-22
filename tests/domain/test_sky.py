from datetime import datetime

import pytest

from scrolly.domain.sky import Body, sky_at
from scrolly.domain.sunset import SunsetPrefs

KEPT = SunsetPrefs(enabled=True, invited=True, hour=20, minute=0)


def _at(text: str) -> datetime:
    return datetime.fromisoformat(f"2026-10-22T{text}:00+02:00")


@pytest.mark.parametrize(
    ("now", "body", "progress"),
    [
        ("05:00", Body.SUN, 0.0),  # before the morning the sun waits at the start of its arc
        ("06:00", Body.SUN, 0.0),
        ("13:00", Body.SUN, 0.5),
        ("20:00", Body.MOON, 0.0),
        ("22:00", Body.MOON, 0.25),
    ],
)
def test_the_sun_crosses_to_the_sunset_then_the_moon_to_four(
    now: str, body: Body, progress: float
) -> None:
    sky = sky_at(_at(now), KEPT)
    assert sky.body is body
    assert sky.progress == pytest.approx(progress)


def test_after_midnight_the_moon_is_still_on_the_same_logical_day() -> None:
    sky = sky_at(datetime.fromisoformat("2026-10-23T02:00:00+02:00"), KEPT)
    assert sky.body is Body.MOON
    assert sky.progress == pytest.approx(0.75)


def test_without_a_sunset_the_default_hour_ends_the_sun() -> None:
    sky = sky_at(_at("21:30"), SunsetPrefs())
    assert sky.body is Body.MOON
