from datetime import datetime, time, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.appearance import Phase
from scrolly.domain.models import Day, TrialState
from scrolly.domain.sunset import (
    FINISHED,
    SunsetError,
    SunsetPrefs,
    budget_sunset,
    day_finished,
    parse_sunset_time,
    phase_at,
    settle_finished,
)
from tests.factories import make_trial

ON = SunsetPrefs(enabled=True, invited=True, hour=21)
SEALED = Day(logical_day=datetime(2026, 10, 18).date(), first_sealed_at=datetime(2026, 10, 18, 9))


def at(text: str, day: str = "2026-10-18") -> datetime:
    return datetime.fromisoformat(f"{day}T{text}:00+02:00")


@pytest.mark.parametrize(
    ("moment", "expected"),
    [
        (at("13:00"), Phase.DAY),
        (at("19:59"), Phase.DAY),
        (at("20:00"), Phase.GOLDEN),
        (at("20:59"), Phase.GOLDEN),
        (at("21:00"), Phase.DUSK),
        (at("23:30"), Phase.DUSK),
        (at("03:59", "2026-10-19"), Phase.DUSK),  # still the same logical day
        (at("04:00", "2026-10-19"), Phase.DAY),  # the next one
    ],
)
def test_the_phase_follows_the_clock_around_the_sunset(moment: datetime, expected: Phase) -> None:
    assert phase_at(moment, ON, None) is expected


def test_with_no_sunset_the_day_never_changes_colour_by_the_clock() -> None:
    for prefs in (SunsetPrefs(), SunsetPrefs(invited=True, enabled=False)):
        assert phase_at(at("22:00"), prefs, SEALED) is Phase.DAY


def test_a_late_sunset_after_midnight_belongs_to_the_logical_day() -> None:
    prefs = SunsetPrefs(enabled=True, invited=True, hour=1)
    assert phase_at(at("23:30"), prefs, None) is Phase.DAY
    assert phase_at(at("00:30", "2026-10-19"), prefs, None) is Phase.GOLDEN
    assert phase_at(at("01:30", "2026-10-19"), prefs, None) is Phase.DUSK


def test_finishing_the_day_forces_dusk_even_without_a_sunset() -> None:
    forced = Day(logical_day=SEALED.logical_day, dusk_override=FINISHED)
    assert phase_at(at("10:00"), SunsetPrefs(), forced) is Phase.DUSK
    assert phase_at(at("10:00"), ON, forced) is Phase.DUSK


def test_a_day_is_finished_when_sealed_and_nothing_is_open() -> None:
    done = make_trial("A", state=TrialState.DONE)
    let_go = make_trial("B", state=TrialState.LOST)
    assert day_finished(SEALED, [done, let_go])
    assert day_finished(SEALED, [let_go])  # letting everything go counts
    assert not day_finished(SEALED, [done, make_trial("C")])
    assert not day_finished(Day(logical_day=SEALED.logical_day), [done])  # never sealed
    assert not day_finished(None, [])


def test_settling_keeps_dusk_after_a_new_trial_is_scribed() -> None:
    settled = settle_finished(SEALED, [make_trial("A", state=TrialState.DONE)])
    assert settled is not None and settled.dusk_override == FINISHED
    again = settle_finished(settled, [make_trial("A", state=TrialState.DONE), make_trial("New")])
    assert again == settled


def test_settling_an_unfinished_day_changes_nothing() -> None:
    assert settle_finished(SEALED, [make_trial("A")]) == SEALED


def test_the_budget_counts_against_the_default_hour_until_the_user_answers() -> None:
    assert budget_sunset(SunsetPrefs()) == time(21, 0)
    assert budget_sunset(SunsetPrefs(invited=True, enabled=True, hour=19, minute=30)) == time(
        19, 30
    )
    assert budget_sunset(SunsetPrefs(invited=True, enabled=False)) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [("21", time(21)), (" 9:30 ", time(9, 30)), ("21:00", time(21)), ("00:00", time(0))],
)
def test_sunset_times_are_read_in_a_few_spellings(text: str, expected: time) -> None:
    assert parse_sunset_time(text) == expected


@pytest.mark.parametrize("text", ["", "25", "9pm", "21:60", "21.30", "-1"])
def test_unreadable_sunset_times_are_refused_with_a_hint(text: str) -> None:
    with pytest.raises(SunsetError, match="21:00"):
        parse_sunset_time(text)


@given(st.integers(0, 23), st.integers(0, 59))
def test_through_a_logical_day_the_phase_only_moves_day_golden_dusk(hour: int, minute: int) -> None:
    prefs = SunsetPrefs(enabled=True, invited=True, hour=hour, minute=minute)
    rank = {Phase.DAY: 0, Phase.GOLDEN: 1, Phase.DUSK: 2}
    start = at("04:00")
    phases = [
        rank[phase_at(start + timedelta(minutes=step), prefs, None)] for step in range(0, 1440, 7)
    ]
    assert phases == sorted(phases)
