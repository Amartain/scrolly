from datetime import datetime, timedelta

from scrolly.domain.models import ArtKind, OriginType, TrialState
from scrolly.domain.purge import purge_today
from scrolly.domain.timer import start
from tests.factories import make_item, make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")


def test_open_trials_are_removed_and_conquered_ones_stay() -> None:
    trials = [
        make_trial("Now", state=TrialState.IMMEDIATE),
        make_trial("Next"),
        make_trial("Done", state=TrialState.DONE),
        make_trial("Later", state=TrialState.POSTPONED),
        make_trial("Gone", state=TrialState.LOST),
    ]
    purged = purge_today(trials, [], NOW)
    assert sorted(purged.removed) == ["trial-Next", "trial-Now"]


def test_mandates_and_horizon_trials_go_back_with_the_time_worked() -> None:
    mandate = start(
        make_trial("Taxes", state=TrialState.IMMEDIATE, is_mandate=True),
        NOW - timedelta(minutes=4),
    )
    summoned = make_trial(
        "Plan", origin_type=OriginType.HORIZON, origin_id="h1", timer_accumulated_s=90
    )
    mortal = make_trial("Chore")
    purged = purge_today([mandate, summoned, mortal], [make_item("Old")], NOW)
    assert [i.title for i in purged.horizon] == ["Taxes", "Plan", "Old"]
    assert purged.horizon[0].worked_s == 4 * 60
    assert purged.horizon[1].worked_s == 90
    assert "trial-Chore" in purged.removed


def test_art_instances_are_just_removed() -> None:
    art = make_trial("Stretch", art_kind=ArtKind.FOUNDATIONAL, origin_type=OriginType.HORIZON)
    purged = purge_today([art], [], NOW)
    assert purged.horizon == [] and purged.removed == ["trial-Stretch"]


def test_nothing_open_changes_nothing() -> None:
    purged = purge_today([make_trial("Done", state=TrialState.DONE)], [make_item("A")], NOW)
    assert purged.removed == [] and [i.title for i in purged.horizon] == ["A"]
