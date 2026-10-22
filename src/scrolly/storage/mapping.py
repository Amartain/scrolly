"""Row <-> domain conversions. ORM rows never leave the storage package."""

from datetime import date, datetime

from scrolly.domain.models import (
    Art,
    ArtKind,
    Day,
    HorizonItem,
    OriginType,
    Trial,
    TrialState,
)
from scrolly.storage.tables import ArtRow, DayRow, HorizonItemRow, TrialRow
from scrolly.storage.timestamps import from_iso, utc_iso


def _iso(moment: datetime | None) -> str | None:
    return None if moment is None else utc_iso(moment)


def _kind(value: str | None) -> ArtKind | None:
    return None if value is None else ArtKind(value)


def _kind_value(kind: ArtKind | None) -> str | None:
    return None if kind is None else kind.value


def trial_from_row(row: TrialRow) -> Trial:
    return Trial(
        id=row.id,
        logical_day=date.fromisoformat(row.logical_day),
        title=row.title,
        state=TrialState(row.state),
        is_mandate=row.is_mandate,
        origin_type=OriginType(row.origin_type),
        origin_id=row.origin_id,
        position=row.position,
        essence_expected_min=row.essence_expected_min,
        essence_actual_min=row.essence_actual_min,
        completed_at=from_iso(row.completed_at),
        note=row.note,
        timer_started_at=from_iso(row.timer_started_at),
        timer_paused_at=from_iso(row.timer_paused_at),
        timer_accumulated_s=row.timer_accumulated_s,
        qi_expected=row.qi_expected,
        qi_actual=row.qi_actual,
        art_kind=_kind(row.art_kind),
    )


def apply_trial(row: TrialRow, trial: Trial) -> None:
    row.logical_day = trial.logical_day.isoformat()
    row.title = trial.title
    row.state = trial.state.value
    row.is_mandate = trial.is_mandate
    row.origin_type = trial.origin_type.value
    row.origin_id = trial.origin_id
    row.position = trial.position
    row.essence_expected_min = trial.essence_expected_min
    row.essence_actual_min = trial.essence_actual_min
    row.completed_at = _iso(trial.completed_at)
    row.note = trial.note
    row.timer_started_at = _iso(trial.timer_started_at)
    row.timer_paused_at = _iso(trial.timer_paused_at)
    row.timer_accumulated_s = trial.timer_accumulated_s
    row.qi_expected = trial.qi_expected
    row.qi_actual = trial.qi_actual
    row.art_kind = _kind_value(trial.art_kind)


def horizon_from_row(row: HorizonItemRow) -> HorizonItem:
    return HorizonItem(
        id=row.id,
        title=row.title,
        is_mandate=row.is_mandate,
        essence_expected_min=row.essence_expected_min,
        note=row.note,
        origin_type=OriginType(row.origin_type),
        origin_id=row.origin_id,
        qi_expected=row.qi_expected,
        art_kind=_kind(row.art_kind),
        worked_s=row.worked_s,
    )


def apply_horizon(row: HorizonItemRow, item: HorizonItem, position: int) -> None:
    row.title = item.title
    row.is_mandate = item.is_mandate
    row.essence_expected_min = item.essence_expected_min
    row.note = item.note
    row.position = position
    row.origin_type = item.origin_type.value
    row.origin_id = item.origin_id
    row.qi_expected = item.qi_expected
    row.art_kind = _kind_value(item.art_kind)
    row.worked_s = item.worked_s


def art_from_row(row: ArtRow) -> Art:
    return Art(
        id=row.id,
        kind=ArtKind(row.kind),
        title=row.title,
        essence_expected_min=row.essence_expected_min,
        note=row.note,
        qi_expected=row.qi_expected,
    )


def apply_art(row: ArtRow, art: Art, position: int) -> None:
    row.kind = art.kind.value
    row.title = art.title
    row.essence_expected_min = art.essence_expected_min
    row.note = art.note
    row.position = position
    row.qi_expected = art.qi_expected


def day_from_row(row: DayRow) -> Day:
    return Day(
        logical_day=date.fromisoformat(row.logical_day),
        first_sealed_at=from_iso(row.first_sealed_at),
        rolled_over_at=from_iso(row.rolled_over_at),
        dusk_override=row.dusk_override,
        advisor_silenced=row.advisor_silenced,
        qi_start=row.qi_start,
        poem_shown_at=from_iso(row.poem_shown_at),
        victory_seen_at=from_iso(row.victory_seen_at),
        planning_started_at=from_iso(row.planning_started_at),
        planning_accumulated_s=row.planning_accumulated_s,
    )


def apply_day(row: DayRow, day: Day) -> None:
    row.logical_day = day.logical_day.isoformat()
    row.first_sealed_at = _iso(day.first_sealed_at)
    row.rolled_over_at = _iso(day.rolled_over_at)
    row.dusk_override = day.dusk_override
    row.advisor_silenced = day.advisor_silenced
    row.qi_start = day.qi_start
    row.poem_shown_at = _iso(day.poem_shown_at)
    row.victory_seen_at = _iso(day.victory_seen_at)
    row.planning_started_at = _iso(day.planning_started_at)
    row.planning_accumulated_s = day.planning_accumulated_s
