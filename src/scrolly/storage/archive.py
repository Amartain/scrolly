"""The whole database as plain tables: read it for Backup Scroll, write it back for Restore Scroll.

Every table is described by its SQLAlchemy columns, so a column added in a migration is carried
without touching this file.
"""

from typing import Any

from sqlalchemy import Boolean, Column, Integer, delete, insert, select
from sqlalchemy import Table as SqlTable
from sqlalchemy.orm import Session

from scrolly.domain.archive import ArchiveError, Row, Table, Tables
from scrolly.storage.tables import Base

_TRUE = {"true", "1", "yes"}
_FALSE = {"false", "0", "no", ""}


def _text(column: Column[Any], value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(column.type, Boolean):
        return "true" if value else "false"
    return str(value)


def _value(column: Column[Any], text: str | None) -> Any:
    """Text from a file back to the column's type. An empty cell is None, or the default."""
    if text is None or (text == "" and not isinstance(column.type, Boolean)):
        if column.nullable:
            return None
        default = getattr(column.default, "arg", None)
        if default is not None:
            return default
        if isinstance(column.type, Integer):
            return 0
        if column.primary_key or column.name in {"created_at", "updated_at", "title"}:
            raise ArchiveError(f"A row has no {column.name}")
        return ""
    if isinstance(column.type, Boolean):
        lowered = text.strip().lower()
        if lowered not in _TRUE | _FALSE:
            raise ArchiveError(f"{column.name} must be true or false, not {text!r}")
        return lowered in _TRUE
    if isinstance(column.type, Integer):
        try:
            return int(text)
        except ValueError as error:
            raise ArchiveError(f"{column.name} must be a whole number, not {text!r}") from error
    return text


def _sql_table(name: str) -> SqlTable:
    table = Base.metadata.tables.get(name)
    if table is None:
        raise ArchiveError(f"This file holds a table Scrolly does not know: {name}")
    return table


def _records(name: str, table: Table) -> list[dict[str, Any]]:
    sql = _sql_table(name)
    unknown = [c for c in table.columns if c not in sql.columns]
    if unknown:
        raise ArchiveError(f"{name} has a column Scrolly does not know: {unknown[0]}")
    return [{c.name: _value(c, row.get(c.name)) for c in sql.columns} for row in table.rows]


class SqlArchive:
    def __init__(self, session: Session) -> None:
        self._session = session

    def dump(self) -> Tables:
        tables: Tables = {}
        for sql in Base.metadata.sorted_tables:
            columns = tuple(c.name for c in sql.columns)
            result = self._session.execute(select(sql).order_by(*sql.primary_key.columns))
            rows: list[Row] = [
                {c.name: _text(c, record[c.name]) for c in sql.columns}
                for record in result.mappings()
            ]
            tables[sql.name] = Table(columns, rows)
        return tables

    def replace_all(self, tables: Tables) -> int:
        """Make the database exactly these tables. Checked first, so a bad file changes nothing."""
        prepared = {name: _records(name, table) for name, table in tables.items()}
        for sql in reversed(Base.metadata.sorted_tables):
            self._session.execute(delete(sql))
        total = 0
        for sql in Base.metadata.sorted_tables:
            records = prepared.get(sql.name, [])
            if records:
                self._session.execute(insert(sql), records)
            total += len(records)
        self._session.expire_all()
        return total

    def add_missing(self, tables: Tables) -> tuple[int, int]:
        """Add rows whose id is new. Returns (added, skipped)."""
        added = skipped = 0
        for name, table in tables.items():
            sql = _sql_table(name)
            records = _records(name, table)
            known = set(self._session.execute(select(sql.c.id)).scalars())
            fresh = [r for r in records if r["id"] not in known]
            if fresh:
                self._session.execute(insert(sql), fresh)
            added += len(fresh)
            skipped += len(records) - len(fresh)
        self._session.expire_all()
        return added, skipped
