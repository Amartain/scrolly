import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from scrolly.domain.merge import ImportBatch
from scrolly.domain.models import ArtKind, OriginType, TrialState
from scrolly.io.errors import ImportFormatError
from scrolly.io.import_prototype_json import parse_prototype_json

FIXTURE = Path(__file__).parent.parent / "fixtures" / "prototype_backup.json"


@pytest.fixture
def batch() -> ImportBatch:
    return parse_prototype_json(FIXTURE.read_text(encoding="utf-8"))


def test_counts(batch: ImportBatch) -> None:
    assert (len(batch.trials), len(batch.horizon), len(batch.arts)) == (7, 3, 3)


def test_status_maps_to_the_rebuild_states(batch: ImportBatch) -> None:
    states = {t.title: t.state for t in batch.trials}
    assert states["Morning stretch"] is TrialState.DONE
    assert states["Write report"] is TrialState.IMMEDIATE
    assert states["Tidy desk"] is TrialState.REMAINING
    assert states["Skipped errand"] is TrialState.LOST
    assert states["Call plumber"] is TrialState.POSTPONED


def test_a_done_trial_keeps_time_and_completion(batch: ImportBatch) -> None:
    stretch = next(t for t in batch.trials if t.title == "Morning stretch")
    assert stretch.essence_expected_min == 15 and stretch.essence_actual_min == 20
    assert stretch.timer_accumulated_s == 1187
    assert stretch.completed_at == datetime.fromtimestamp(1792323198.021, UTC)
    assert stretch.logical_day == date(2026, 10, 18)


def test_origin_comes_from_the_ritual_and_restorative_flags(batch: ImportBatch) -> None:
    origins = {t.title: t.origin_type for t in batch.trials}
    assert origins["Morning stretch"] is OriginType.FOUNDATIONAL_ART
    assert origins["Afternoon tea"] is OriginType.RESTORATIVE_ART
    assert origins["Tidy desk"] is OriginType.BRAIN_DUMP


def test_zero_estimate_means_no_estimate_and_a_timer_fills_a_missing_actual(
    batch: ImportBatch,
) -> None:
    tidy = next(t for t in batch.trials if t.title == "Tidy desk")
    tea = next(t for t in batch.trials if t.title == "Afternoon tea")
    assert tidy.essence_expected_min is None
    assert tea.essence_expected_min is None and tea.essence_actual_min == 43


def test_old_history_rows_without_the_newer_fields_load(batch: ImportBatch) -> None:
    cat = next(t for t in batch.trials if t.title == "Feed the cat")
    assert not cat.is_mandate and cat.completed_at is None and cat.timer_accumulated_s == 0
    assert cat.essence_actual_min == 10


def test_only_done_trials_keep_an_actual(batch: ImportBatch) -> None:
    report = next(t for t in batch.trials if t.title == "Write report")
    assert report.essence_actual_min is None and report.is_mandate


def test_arts_and_horizon(batch: ImportBatch) -> None:
    kinds = {a.title: a.kind for a in batch.arts}
    assert kinds["Callisthenics"] is ArtKind.FOUNDATIONAL
    assert kinds["Meditation"] is ArtKind.RESTORATIVE
    assert batch.horizon[0].title == "Plan the garden"
    assert batch.horizon[0].is_mandate and batch.horizon[0].essence_expected_min == 45


def test_ids_are_stable_so_a_second_import_matches() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    first, second = parse_prototype_json(text), parse_prototype_json(text)
    assert [t.id for t in first.trials] == [t.id for t in second.trials]
    assert len({t.id for t in first.trials}) == len(first.trials)


def test_a_bare_list_is_recognised_by_file_name_or_id_prefix() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    future = parse_prototype_json(json.dumps(data["future"]), "future_trials")
    assert len(future.horizon) == 3 and future.trials == []
    rituals = parse_prototype_json(json.dumps(data["rituals"]), "anything")
    assert [a.kind for a in rituals.arts] == [ArtKind.FOUNDATIONAL] * 2
    restorations = parse_prototype_json(json.dumps(data["restorations"]))
    assert [a.kind for a in restorations.arts] == [ArtKind.RESTORATIVE]
    history = parse_prototype_json(json.dumps(data["history"]))
    assert len(history.trials) == 4


@pytest.mark.parametrize("text", ["not json", "42", '{"hello": []}', '[{"id": "q_1"}]'])
def test_bad_input_raises_a_readable_error(text: str) -> None:
    with pytest.raises(ImportFormatError):
        parse_prototype_json(text)
