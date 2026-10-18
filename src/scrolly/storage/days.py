import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.models import Day
from scrolly.storage.mapping import apply_day, day_from_row
from scrolly.storage.tables import DayRow
from scrolly.storage.timestamps import utc_iso


class SqlDays:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _row(self, day: date) -> DayRow | None:
        query = select(DayRow).where(
            DayRow.realm_id == REALM_DEFAULT, DayRow.logical_day == day.isoformat()
        )
        return self._session.scalars(query).first()

    def get(self, day: date) -> Day | None:
        row = self._row(day)
        return None if row is None else day_from_row(row)

    def list_all(self) -> list[Day]:
        query = select(DayRow).where(DayRow.realm_id == REALM_DEFAULT).order_by(DayRow.logical_day)
        return [day_from_row(row) for row in self._session.scalars(query)]

    def save(self, day: Day, now: datetime) -> None:
        row = self._row(day.logical_day)
        is_new = row is None
        if row is None:
            row = DayRow(id=str(uuid.uuid4()), realm_id=REALM_DEFAULT, created_at=utc_iso(now))
        apply_day(row, day)
        row.updated_at = utc_iso(now)
        if is_new:
            self._session.add(row)
        self._session.flush()
