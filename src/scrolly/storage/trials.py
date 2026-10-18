from collections.abc import Sequence
from datetime import date, datetime

from sqlalchemy import ColumnElement, delete, select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.models import Trial, TrialState
from scrolly.storage.mapping import apply_trial, trial_from_row
from scrolly.storage.tables import TrialRow
from scrolly.storage.timestamps import utc_iso


class SqlTrials:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _rows(self, *conditions: ColumnElement[bool]) -> list[TrialRow]:
        query = (
            select(TrialRow)
            .where(TrialRow.realm_id == REALM_DEFAULT, *conditions)
            .order_by(TrialRow.logical_day, TrialRow.position)
        )
        return list(self._session.scalars(query))

    def list_all(self) -> list[Trial]:
        return [trial_from_row(row) for row in self._rows()]

    def list_open_before(self, day: date) -> list[Trial]:
        open_states = [TrialState.IMMEDIATE.value, TrialState.REMAINING.value]
        rows = self._rows(TrialRow.state.in_(open_states), TrialRow.logical_day < day.isoformat())
        return [trial_from_row(row) for row in rows]

    def list_for_day(self, day: date) -> list[Trial]:
        return [trial_from_row(row) for row in self._rows(TrialRow.logical_day == day.isoformat())]

    def delete(self, ids: Sequence[str]) -> None:
        self._session.execute(delete(TrialRow).where(TrialRow.id.in_(list(ids))))
        self._session.flush()

    def save(self, trials: Sequence[Trial], now: datetime) -> None:
        for trial in trials:
            row = self._session.get(TrialRow, trial.id)
            is_new = row is None
            if row is None:
                row = TrialRow(id=trial.id, realm_id=REALM_DEFAULT, created_at=utc_iso(now))
            apply_trial(row, trial)
            row.updated_at = utc_iso(now)
            if is_new:
                self._session.add(row)
        self._session.flush()
