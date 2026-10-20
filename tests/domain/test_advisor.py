from datetime import datetime, timedelta

import pytest

from scrolly.domain.advisor import advisor_due, postponable_mandates, remaining_expected_min
from scrolly.domain.appearance import Phase
from scrolly.domain.models import TrialState
from scrolly.domain.queue import postpone_mandates
from scrolly.domain.sunset import SunsetPrefs
from scrolly.domain.timer import start
from tests.factories import make_item, make_trial

ON = SunsetPrefs(enabled=True, invited=True, hour=21)
NOW = datetime.fromisoformat("2026-10-18T19:00:00+02:00")


def test_the_advisor_speaks_only_when_the_plan_runs_past_sunset() -> None:
    assert not advisor_due(NOW, ON, Phase.DAY, 119, silenced=False)
    assert not advisor_due(NOW, ON, Phase.DAY, 120, silenced=False)  # ends exactly at sunset
    assert advisor_due(NOW, ON, Phase.DAY, 121, silenced=False)
    assert advisor_due(NOW, ON, Phase.GOLDEN, 121, silenced=False)


@pytest.mark.parametrize(
    ("prefs", "phase", "silenced", "minutes"),
    [
        (SunsetPrefs(), Phase.DAY, False, 500),  # no sunset kept
        (SunsetPrefs(invited=True), Phase.DAY, False, 500),  # said "not now"
        (ON, Phase.DUSK, False, 500),  # after sunset: totals only
        (ON, Phase.DAY, True, 500),  # not again today
        (ON, Phase.DAY, False, 0),  # nothing planned
    ],
)
def test_the_advisor_stays_quiet_otherwise(
    prefs: SunsetPrefs, phase: Phase, silenced: bool, minutes: int
) -> None:
    assert not advisor_due(NOW, prefs, phase, minutes, silenced)


def test_only_open_estimates_count() -> None:
    trials = [
        make_trial("Now", state=TrialState.IMMEDIATE, essence_expected_min=30),
        make_trial("Next", essence_expected_min=45),
        make_trial("Unknown"),
        make_trial("Done", state=TrialState.DONE, essence_expected_min=600),
    ]
    assert remaining_expected_min(trials) == 75


def test_postponing_mandates_leaves_the_immediate_trial_and_keeps_order() -> None:
    now = start(make_trial("Now", state=TrialState.IMMEDIATE, is_mandate=True), NOW)
    first = make_trial("First", is_mandate=True, position=1)
    second = make_trial("Second", is_mandate=True, position=2)
    mortal = make_trial("Mortal", position=3)
    trials = [now, second, mortal, first]
    assert [t.title for t in postponable_mandates(trials)] == ["First", "Second"]

    changed, horizon = postpone_mandates(trials, [make_item("Old")], NOW + timedelta(minutes=1))
    assert {t.title for t in changed} == {"First", "Second"}
    assert all(t.state is TrialState.POSTPONED for t in changed)
    assert [item.title for item in horizon] == ["First", "Second", "Old"]
    assert all(item.is_mandate for item in horizon[:2])


def test_with_no_waiting_mandates_nothing_changes() -> None:
    trials = [make_trial("Now", state=TrialState.IMMEDIATE, is_mandate=True), make_trial("M")]
    changed, horizon = postpone_mandates(trials, [], NOW)
    assert changed == [] and horizon == []
