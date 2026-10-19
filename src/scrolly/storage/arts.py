from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.models import Art
from scrolly.storage.mapping import apply_art, art_from_row
from scrolly.storage.tables import ArtRow
from scrolly.storage.timestamps import utc_iso


class SqlArts:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Art]:
        query = select(ArtRow).where(ArtRow.realm_id == REALM_DEFAULT).order_by(ArtRow.position)
        return [art_from_row(row) for row in self._session.scalars(query)]

    def save(self, arts: Sequence[Art], now: datetime) -> None:
        """Add or update. New Arts go after the existing ones."""
        last = self._session.scalar(select(func.max(ArtRow.position)))
        position = 0 if last is None else last + 1
        for art in arts:
            row = self._session.get(ArtRow, art.id)
            is_new = row is None
            if row is None:
                row = ArtRow(id=art.id, realm_id=REALM_DEFAULT, created_at=utc_iso(now))
                apply_art(row, art, position)
                position += 1
            else:
                apply_art(row, art, row.position)
            row.updated_at = utc_iso(now)
            if is_new:
                self._session.add(row)
        self._session.flush()

    def set_order(self, ids: Sequence[str], now: datetime) -> None:
        """Put the Arts in exactly this order."""
        for position, art_id in enumerate(ids):
            row = self._session.get(ArtRow, art_id)
            if row is not None:
                row.position = position
                row.updated_at = utc_iso(now)
        self._session.flush()
