from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.segments import Discipline, Segment
from scrolly.storage.tables import TimerSegmentRow
from scrolly.storage.timestamps import from_iso, utc_iso


def _segment(row: TimerSegmentRow) -> Segment:
    started = from_iso(row.started_at)
    assert started is not None
    return Segment(
        row.id, row.trial_id, Discipline(row.discipline), started, from_iso(row.ended_at)
    )


class SqlSegments:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _rows(self, *conditions: object) -> list[TimerSegmentRow]:
        query = (
            select(TimerSegmentRow)
            .where(TimerSegmentRow.realm_id == REALM_DEFAULT, *conditions)  # type: ignore[arg-type]
            .order_by(TimerSegmentRow.started_at)
        )
        return list(self._session.scalars(query))

    def list_open(self) -> list[Segment]:
        return [_segment(row) for row in self._rows(TimerSegmentRow.ended_at.is_(None))]

    def list_for_trial(self, trial_id: str) -> list[Segment]:
        return [_segment(row) for row in self._rows(TimerSegmentRow.trial_id == trial_id)]

    def delete_for_trials(self, trial_ids: Sequence[str]) -> None:
        self._session.execute(
            delete(TimerSegmentRow).where(TimerSegmentRow.trial_id.in_(list(trial_ids)))
        )
        self._session.flush()

    def save(self, segments: Sequence[Segment], now: datetime) -> None:
        for segment in segments:
            row = self._session.get(TimerSegmentRow, segment.id)
            if row is None:
                row = TimerSegmentRow(
                    id=segment.id, realm_id=REALM_DEFAULT, created_at=utc_iso(now)
                )
                self._session.add(row)
            row.trial_id = segment.trial_id
            row.discipline = segment.discipline.value
            row.started_at = utc_iso(segment.started_at)
            row.ended_at = None if segment.ended_at is None else utc_iso(segment.ended_at)
            row.updated_at = utc_iso(now)
        self._session.flush()
