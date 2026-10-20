from datetime import date, datetime, timedelta

import pytest

from scrolly.domain.models import ArtKind, Day, OriginType, TrialState
from scrolly.domain.restart import restart_today
from scrolly.domain.secret_seals import Seal, SealKind, parse_seal
from scrolly.domain.timer import start
from tests.factories import make_item, make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("dusk", Seal(SealKind.DUSK)),
        ("  DUSK ", Seal(SealKind.DUSK)),
        ("sunrise", Seal(SealKind.SUNRISE)),
        ("4AM", Seal(SealKind.ROLLOVER)),
        ("4am", Seal(SealKind.ROLLOVER)),
        ("restart-today", Seal(SealKind.RESTART)),
        ("Restart-Today", Seal(SealKind.RESTART)),
        ("arise", Seal(SealKind.DAY, 100)),
        ("day 10", Seal(SealKind.DAY, 10)),
        ("Day   21", Seal(SealKind.DAY, 21)),
        ("7", Seal(SealKind.DAY, 7)),
        ("4", Seal(SealKind.DAY, 4)),
    ],
)
def test_the_words_each_name_a_seal(text: str, expected: Seal) -> None:
    assert parse_seal(text) == expected


@pytest.mark.parametrize(
    "text",
    ["", "hello", "day", "day x", "0", "day 0", "-3", "10000", "restart", "dusk now", "4 am"],
)
def test_other_words_name_nothing(text: str) -> None:
    assert parse_seal(text) is None


def test_restarting_removes_every_trial_and_unseals_the_day() -> None:
    sealed = Day(
        logical_day=date(2026, 10, 18),
        first_sealed_at=NOW,
        rolled_over_at=NOW,
        qi_start=90,
        dusk_override="dusk",
        advisor_silenced=True,
        poem_shown_at=NOW,
    )
    trials = [
        make_trial("Done", state=TrialState.DONE),
        make_trial("Now", state=TrialState.IMMEDIATE),
        make_trial("Later", state=TrialState.POSTPONED),
    ]
    result = restart_today(trials, [], sealed, NOW)
    assert sorted(result.removed) == ["trial-Done", "trial-Later", "trial-Now"]
    day = result.day
    assert (day.first_sealed_at, day.qi_start, day.dusk_override, day.poem_shown_at) == (
        None,
        None,
        None,
        None,
    )
    assert day.advisor_silenced is False
    assert day.rolled_over_at == NOW  # the rollover already done is not run again


def test_what_was_called_down_from_the_horizon_goes_back_with_its_time() -> None:
    timed = start(
        make_trial(
            "Plan", state=TrialState.IMMEDIATE, origin_type=OriginType.HORIZON, origin_id="h1"
        ),
        NOW - timedelta(minutes=3),
    )
    conquered = make_trial(
        "Idea",
        state=TrialState.DONE,
        origin_type=OriginType.HORIZON,
        origin_id="h2",
        timer_accumulated_s=600,
    )
    typed = make_trial("Typed in")
    art = make_trial("Stretch", art_kind=ArtKind.FOUNDATIONAL, origin_type=OriginType.HORIZON)
    postponed = make_trial(
        "Moved on", state=TrialState.POSTPONED, origin_type=OriginType.HORIZON, origin_id="h3"
    )
    day = Day(logical_day=date(2026, 10, 18), first_sealed_at=NOW)
    result = restart_today([timed, conquered, typed, art, postponed], [make_item("Old")], day, NOW)
    assert sorted(i.title for i in result.horizon) == ["Idea", "Old", "Plan"]
    by_title = {i.title: i for i in result.horizon}
    assert by_title["Plan"].worked_s == 180 and by_title["Idea"].worked_s == 600
