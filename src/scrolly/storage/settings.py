import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from scrolly.config import REALM_DEFAULT
from scrolly.storage.tables import SettingRow


def _utc_iso(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat()


class SqlSettings:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _row(self, key: str) -> SettingRow | None:
        query = select(SettingRow).where(
            SettingRow.realm_id == REALM_DEFAULT, SettingRow.key == key
        )
        return self._session.scalars(query).first()

    def get(self, key: str) -> dict[str, Any] | None:
        row = self._row(key)
        return None if row is None else json.loads(row.value_json)

    def set(self, key: str, value: dict[str, Any], now: datetime) -> None:
        row = self._row(key)
        if row is None:
            row = SettingRow(
                id=str(uuid.uuid4()),
                realm_id=REALM_DEFAULT,
                key=key,
                created_at=_utc_iso(now),
            )
            self._session.add(row)
        row.value_json = json.dumps(value)
        row.updated_at = _utc_iso(now)
        self._session.flush()
