from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.scraps import Scrap
from scrolly.storage.tables import BambooScrapRow
from scrolly.storage.timestamps import from_iso, utc_iso


def _scrap(row: BambooScrapRow) -> Scrap:
    opened, saved = from_iso(row.opened_at), from_iso(row.saved_at)
    assert opened is not None and saved is not None
    ids = tuple(i for i in row.trial_ids.split(",") if i)
    return Scrap(row.id, opened, saved, from_iso(row.closed_at), row.text, ids)


class SqlScraps:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Scrap]:
        query = (
            select(BambooScrapRow)
            .where(BambooScrapRow.realm_id == REALM_DEFAULT)
            .order_by(BambooScrapRow.opened_at)
        )
        return [_scrap(row) for row in self._session.scalars(query)]

    def save(self, scrap: Scrap, now: datetime) -> None:
        row = self._session.get(BambooScrapRow, scrap.id)
        if row is None:
            row = BambooScrapRow(id=scrap.id, realm_id=REALM_DEFAULT, created_at=utc_iso(now))
            self._session.add(row)
        row.opened_at = utc_iso(scrap.opened_at)
        row.saved_at = utc_iso(scrap.saved_at)
        row.closed_at = None if scrap.closed_at is None else utc_iso(scrap.closed_at)
        row.text = scrap.text
        row.trial_ids = ",".join(scrap.trial_ids)
        row.updated_at = utc_iso(now)
        self._session.flush()

    def delete(self, scrap_id: str) -> None:
        self._session.execute(delete(BambooScrapRow).where(BambooScrapRow.id == scrap_id))
        self._session.flush()
