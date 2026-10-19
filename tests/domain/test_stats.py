from datetime import date, datetime

from scrolly.domain.models import Day, TrialState
from scrolly.domain.stats import heavenly_cycles, lifetime_conquered
from tests.factories import make_trial

SEALED = datetime.fromisoformat("2026-10-18T09:00:00+02:00")


def test_lifetime_conquered_counts_done_trials_on_every_day() -> None:
    trials = [
        make_trial("a", state=TrialState.DONE),
        make_trial("b", state=TrialState.DONE, logical_day=date(2026, 9, 1)),
        make_trial("c", state=TrialState.REMAINING),
        make_trial("d", state=TrialState.LOST),
    ]
    assert lifetime_conquered(trials) == 2


def test_lifetime_conquered_of_nothing_is_zero() -> None:
    assert lifetime_conquered([]) == 0


def test_heavenly_cycles_count_only_sealed_days() -> None:
    days = [
        Day(logical_day=date(2026, 10, 16), first_sealed_at=SEALED),
        Day(logical_day=date(2026, 10, 17), first_sealed_at=None),
        Day(logical_day=date(2026, 10, 18), first_sealed_at=SEALED),
    ]
    assert heavenly_cycles(days) == 2
