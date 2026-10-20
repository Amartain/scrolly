"""The whole database as plain tables, for Backup Scroll and Restore Scroll. No rule lives here."""

from dataclasses import dataclass, field

Row = dict[str, str | None]


class ArchiveError(ValueError):
    """A backup or CSV that cannot be used. The message is shown to the user."""


@dataclass(frozen=True)
class Table:
    """One table: its columns (so an empty table still has a header) and its rows as text.

    A missing value is None. Booleans are `true` / `false`, numbers are digits.
    """

    columns: tuple[str, ...]
    rows: list[Row] = field(default_factory=list)


Tables = dict[str, Table]


@dataclass(frozen=True)
class Archive:
    """Tables read from a file. A zip replaces the data; a single CSV only adds what is new."""

    tables: Tables
    replaces: bool
