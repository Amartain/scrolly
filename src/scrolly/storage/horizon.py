from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.domain.models import HorizonItem
from scrolly.storage.mapping import apply_horizon, horizon_from_row
from scrolly.storage.tables import HorizonItemRow
from scrolly.storage.timestamps import utc_iso


class SqlHorizon:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _rows(self) -> list[HorizonItemRow]:
        query = (
            select(HorizonItemRow)
            .where(HorizonItemRow.realm_id == REALM_DEFAULT)
            .order_by(HorizonItemRow.position)
        )
        return list(self._session.scalars(query))

    def list_all(self) -> list[HorizonItem]:
        return [horizon_from_row(row) for row in self._rows()]

    def replace_all(self, items: Sequence[HorizonItem], now: datetime) -> None:
        """Make the stored Horizon exactly `items`, in this order."""
        old = {row.id: row for row in self._rows()}
        for position, item in enumerate(items):
            row = old.pop(item.id, None)
            is_new = row is None
            if row is None:
                row = HorizonItemRow(
                    id=item.id,
                    realm_id=REALM_DEFAULT,
                    created_at=utc_iso(now),
                )
            apply_horizon(row, item, position)
            row.updated_at = utc_iso(now)
            if is_new:
                self._session.add(row)
        for leftover in old.values():
            self._session.delete(leftover)
        self._session.flush()
