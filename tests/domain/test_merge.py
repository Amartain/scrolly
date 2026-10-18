from collections.abc import Sequence
from datetime import date, datetime

from scrolly.domain.merge import Existing, ImportBatch, MergeResult, merge_import
from scrolly.domain.models import Art, ArtKind, Day, HorizonItem, Trial, TrialState
from tests.factories import DAY, make_item, make_trial

NOW = datetime.fromisoformat("2026-10-18T13:12:00+02:00")
PAST = date(2026, 10, 7)


def _existing(
    trials: Sequence[Trial] = (),
    horizon: Sequence[HorizonItem] = (),
    arts: Sequence[Art] = (),
    days: Sequence[Day] = (),
) -> Existing:
    return Existing(trials=trials, horizon=horizon, arts=arts, days=days)


def _merge(existing: Existing, batch: ImportBatch) -> MergeResult:
    return merge_import(existing, batch, DAY, NOW)


def test_importing_the_same_batch_twice_adds_nothing() -> None:
    batch = ImportBatch(
        trials=[make_trial("Walk", logical_day=PAST, state=TrialState.DONE)],
        horizon=[make_item("Read")],
        arts=[Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch")],
    )
    first = _merge(_existing(), batch)
    second = _merge(
        _existing(trials=first.trials, horizon=first.horizon, arts=first.arts, days=first.days),
        batch,
    )
    assert (second.summary.added, second.summary.skipped) == (0, 3)
    assert second.days == []


def test_a_trial_with_the_same_day_and_title_is_skipped_even_with_another_id() -> None:
    have = make_trial("Walk", id="x", logical_day=PAST)
    batch = ImportBatch(trials=[make_trial(" walk ", id="y", logical_day=PAST)])
    result = _merge(_existing(trials=[have]), batch)
    assert result.trials == [] and result.summary.trials_skipped == 1


def test_the_same_title_on_another_day_is_kept() -> None:
    have = make_trial("Walk", id="x", logical_day=PAST)
    batch = ImportBatch(trials=[make_trial("Walk", id="y", logical_day=date(2026, 10, 8))])
    assert len(_merge(_existing(trials=[have]), batch).trials) == 1


def test_horizon_duplicates_by_title_are_dropped_including_inside_the_batch() -> None:
    batch = ImportBatch(horizon=[make_item("Plan", id="1"), make_item(" PLAN", id="2")])
    result = _merge(_existing(horizon=[make_item("Read")]), batch)
    assert [i.title for i in result.horizon] == ["Read", "Plan"]
    assert (result.summary.horizon_added, result.summary.horizon_skipped) == (1, 1)


def test_arts_dedup_by_kind_and_title() -> None:
    have = Art(id="a", kind=ArtKind.FOUNDATIONAL, title="Stretch")
    batch = ImportBatch(
        arts=[
            Art(id="b", kind=ArtKind.FOUNDATIONAL, title="stretch"),
            Art(id="c", kind=ArtKind.RESTORATIVE, title="Stretch"),
        ]
    )
    result = _merge(_existing(arts=[have]), batch)
    assert [a.id for a in result.arts] == ["c"]


def test_a_second_immediate_trial_waits_at_the_top_of_remaining() -> None:
    now_trial = make_trial("Now", state=TrialState.IMMEDIATE)
    queued = make_trial("Queued", state=TrialState.REMAINING, position=3)
    incoming = make_trial("Imported", id="i", state=TrialState.IMMEDIATE)
    result = _merge(_existing(trials=[now_trial, queued]), ImportBatch(trials=[incoming]))
    (added,) = result.trials
    assert added.state is TrialState.REMAINING and added.position < queued.position


def test_the_first_immediate_trial_of_the_day_is_kept() -> None:
    incoming = make_trial("Imported", id="i", state=TrialState.IMMEDIATE)
    (added,) = _merge(_existing(), ImportBatch(trials=[incoming])).trials
    assert added.state is TrialState.IMMEDIATE


def test_imported_days_count_as_sealed_days() -> None:
    finished = datetime.fromisoformat("2026-10-07T18:00:00+00:00")
    batch = ImportBatch(
        trials=[
            make_trial("A", id="a", logical_day=PAST, completed_at=finished),
            make_trial("B", id="b", logical_day=date(2026, 10, 8)),
        ]
    )
    days = {d.logical_day: d for d in _merge(_existing(), batch).days}
    assert days[PAST].first_sealed_at == finished
    assert days[date(2026, 10, 8)].first_sealed_at == datetime.fromisoformat(
        "2026-10-08T12:00:00+02:00"
    )


def test_an_already_sealed_day_keeps_its_first_seal() -> None:
    sealed = Day(logical_day=PAST, first_sealed_at=NOW)
    batch = ImportBatch(trials=[make_trial("A", logical_day=PAST)])
    assert _merge(_existing(days=[sealed]), batch).days == []


def test_an_existing_day_row_without_a_seal_gets_one_without_losing_its_fields() -> None:
    day = Day(logical_day=PAST, rolled_over_at=NOW, advisor_silenced=True)
    batch = ImportBatch(trials=[make_trial("A", logical_day=PAST)])
    (updated,) = _merge(_existing(days=[day]), batch).days
    assert updated.first_sealed_at is not None
    assert updated.rolled_over_at == NOW and updated.advisor_silenced
