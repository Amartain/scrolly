"""Backup Scroll: one UTF-8 CSV per table in a zip. Headers are the column names (snake_case)."""

import csv
import io
import zipfile
from datetime import datetime

from scrolly.domain.archive import Table, Tables


def table_csv(table: Table) -> str:
    """A header row, then one row per record. A missing value is an empty cell."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(table.columns)
    for row in table.rows:
        writer.writerow(["" if row.get(name) is None else row[name] for name in table.columns])
    return out.getvalue()


def export_zip(tables: Tables) -> bytes:
    """Every table as `<table>.csv` in one zip."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, table in tables.items():
            archive.writestr(f"{name}.csv", table_csv(table).encode("utf-8"))
    return buffer.getvalue()


def backup_name(now: datetime) -> str:
    return f"scrolly-{now.strftime('%Y%m%d-%H%M%S')}.zip"
