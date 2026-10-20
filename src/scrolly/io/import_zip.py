"""Restore Scroll from a Backup Scroll zip: it replaces what the app holds."""

import io
import zipfile
from pathlib import PurePosixPath

from scrolly.domain.archive import Archive, ArchiveError, Tables
from scrolly.io.import_csv import read_table


def read_zip(content: bytes) -> Archive:
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as error:
        raise ArchiveError("This is not a zip file Scrolly can read") from error
    tables: Tables = {}
    with archive:
        for member in archive.namelist():
            path = PurePosixPath(member)
            if path.suffix.lower() != ".csv" or member.endswith("/"):
                continue
            try:
                text = archive.read(member).decode("utf-8-sig")
            except UnicodeDecodeError as error:
                raise ArchiveError(f"{path.name} is not UTF-8 text") from error
            tables[path.stem] = read_table(text)
    if not tables:
        raise ArchiveError("This zip holds no CSV files from a Scrolly backup")
    return Archive(tables, replaces=True)
