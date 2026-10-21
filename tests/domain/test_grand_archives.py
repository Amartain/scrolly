from datetime import date, datetime, timedelta

from scrolly.domain.grand_archives import archive_days
from scrolly.domain.models import ArtKind, TrialState
from tests.factories import make_trial

TODAY = date(2026, 10, 20)
NOON = datetime.fromisoformat("2026-10-18T12:00:00+02:00")


def _day(offset: int) -> date:
    return TODAY - timedelta(days=offset)


def test_days_come_newest_first_and_today_is_not_among_them() -> None:
    trials = [
        make_trial("Old", logical_day=_day(3), state=TrialState.DONE),
        make_trial("Yesterday", logical_day=_day(1), state=TrialState.DONE),
        make_trial("Today", logical_day=TODAY, state=TrialState.DONE),
    ]
    assert [d.day for d in archive_days(trials, TODAY)] == [_day(1), _day(3)]


def test_each_day_sorts_its_trials_by_what_became_of_them() -> None:
    later = NOON + timedelta(hours=2)
    trials = [
        make_trial("Second", state=TrialState.DONE, completed_at=later),
        make_trial("First", state=TrialState.DONE, completed_at=NOON),
        make_trial("Leaf", state=TrialState.LOST),
        make_trial("Sent", state=TrialState.POSTPONED),
        make_trial("Back", state=TrialState.RETURNED),
    ]
    (day,) = archive_days(trials, TODAY)
    assert [t.title for t in day.conquered] == ["First", "Second"]
    assert [t.title for t in day.lost] == ["Leaf"]
    assert [t.title for t in day.sent_back] == ["Sent", "Back"]
    assert len(day.trials) == 5


def test_a_trial_still_open_from_a_past_day_is_not_archived() -> None:
    trials = [
        make_trial("Open", state=TrialState.REMAINING),
        make_trial("Next", state=TrialState.IMMEDIATE),
    ]
    assert archive_days(trials, TODAY) == []


def test_quiet_days_between_two_cards_are_counted_on_the_older_card() -> None:
    trials = [
        make_trial("A", logical_day=_day(1), state=TrialState.DONE),
        make_trial("B", logical_day=_day(2), state=TrialState.DONE),
        make_trial("C", logical_day=_day(6), state=TrialState.LOST),
    ]
    newest, next_, oldest = archive_days(trials, TODAY)
    assert (newest.rest_before, next_.rest_before, oldest.rest_before) == (0, 0, 3)


def test_days_before_the_first_card_and_after_the_last_are_not_rest() -> None:
    (only,) = archive_days([make_trial("A", logical_day=_day(5), state=TrialState.DONE)], TODAY)
    assert only.rest_before == 0


def test_an_instance_of_an_art_keeps_its_kind() -> None:
    trial = make_trial("Sweep", state=TrialState.DONE, art_kind=ArtKind.RESTORATIVE)
    assert archive_days([trial], TODAY)[0].conquered[0].art_kind is ArtKind.RESTORATIVE
