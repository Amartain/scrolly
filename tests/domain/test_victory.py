from datetime import date, datetime, timedelta
from typing import Any

from scrolly.domain.models import Day, Trial, TrialState
from scrolly.domain.victory import (
    Scene,
    victory_due,
    victory_line,
    victory_scene,
    victory_tally,
)
from tests.factories import make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")
SEALED = Day(logical_day=NOW.date(), first_sealed_at=NOW)


def _done(title: str, at: datetime = NOW, **fields: Any) -> Trial:
    return make_trial(title, state=TrialState.DONE, completed_at=at, **fields)


def test_the_ceremony_is_owed_until_it_is_closed() -> None:
    trials = [_done("A")]
    assert victory_due(SEALED, trials)
    closed = Day(logical_day=NOW.date(), first_sealed_at=NOW, victory_seen_at=NOW)
    assert not victory_due(closed, trials)


def test_a_conquest_after_the_ceremony_earns_it_again() -> None:
    closed = Day(
        logical_day=NOW.date(), first_sealed_at=NOW, victory_seen_at=NOW + timedelta(minutes=1)
    )
    later = [_done("A"), _done("B", NOW + timedelta(minutes=30))]
    assert victory_due(closed, later)


def test_no_ceremony_while_a_trial_is_open_or_the_day_is_not_won() -> None:
    assert not victory_due(SEALED, [_done("A"), make_trial("Waiting")])
    assert not victory_due(SEALED, [make_trial("Gone", state=TrialState.LOST)])
    assert not victory_due(None, [_done("A")])


def test_the_tally_counts_conquests_mandates_and_time() -> None:
    trials = [
        _done("A", essence_actual_min=75, is_mandate=True),
        _done("B", essence_actual_min=45),
        make_trial("Let go", state=TrialState.LOST, essence_actual_min=500),
    ]
    tally = victory_tally(trials)
    assert (tally.conquered, tally.mandates, tally.essence_text) == (2, 1, "2h")


def test_the_lines_take_turns_and_a_day_keeps_its_line() -> None:
    lines = ["a", "b", "c"]
    today = date(2026, 10, 18)
    assert victory_line(today, lines) == victory_line(today, lines)
    assert {victory_line(today + timedelta(days=n), lines) for n in range(3)} == set(lines)


def test_a_day_with_a_conquered_mandate_gets_the_thunder_else_the_wind() -> None:
    assert victory_scene([_done("A"), _done("Duty", is_mandate=True)]) is Scene.THUNDER
    assert victory_scene([_done("A")]) is Scene.WIND
    # A Mandate still open or let go is no tribulation weathered.
    waiting = make_trial("Duty", is_mandate=True, state=TrialState.LOST)
    assert victory_scene([_done("A"), waiting]) is Scene.WIND
