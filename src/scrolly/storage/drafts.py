import uuid
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.models import PlanningDraft, PlanPhase
from scrolly.storage.tables import PlanningDraftRow
from scrolly.storage.timestamps import utc_iso


class SqlDrafts:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _row(self) -> PlanningDraftRow | None:
        query = select(PlanningDraftRow).where(PlanningDraftRow.realm_id == REALM_DEFAULT)
        return self._session.scalars(query).first()

    def get(self) -> PlanningDraft | None:
        row = self._row()
        if row is None:
            return None
        return PlanningDraft(
            logical_day=date.fromisoformat(row.logical_day),
            phase=PlanPhase(row.phase),
            text=row.text,
        )

    def save(self, draft: PlanningDraft, now: datetime) -> None:
        row = self._row()
        is_new = row is None
        if row is None:
            row = PlanningDraftRow(
                id=str(uuid.uuid4()), realm_id=REALM_DEFAULT, created_at=utc_iso(now)
            )
        row.logical_day = draft.logical_day.isoformat()
        row.phase = draft.phase.value
        row.text = draft.text
        row.updated_at = utc_iso(now)
        if is_new:
            self._session.add(row)
        self._session.flush()

    def delete(self) -> None:
        row = self._row()
        if row is not None:
            self._session.delete(row)
            self._session.flush()
