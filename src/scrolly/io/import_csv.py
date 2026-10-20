"""Restore Scroll from one CSV (a table of a backup): rows whose id is new are added."""

import csv
import io

from scrolly.domain.archive import Archive, ArchiveError, Row, Table


def read_table(text: str) -> Table:
    """The header row names the columns; each later row is a record."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if not header or not any(name.strip() for name in header):
        raise ArchiveError("This CSV has no header row")
    columns = tuple(name.strip() for name in header)
    rows: list[Row] = []
    for cells in reader:
        if not any(cell.strip() for cell in cells):
            continue
        rows.append({name: cells[i] if i < len(cells) else None for i, name in enumerate(columns)})
    return Table(columns, rows)


def read_csv(text: str, table_name: str) -> Archive:
    """The file name (`trial.csv`) says which table it is."""
    return Archive({table_name: read_table(text)}, replaces=False)
