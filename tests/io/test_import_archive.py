import io
import zipfile

import pytest

from scrolly.domain.archive import ArchiveError, Table
from scrolly.io.errors import ImportFormatError
from scrolly.io.export_csv import export_zip, table_csv
from scrolly.io.import_csv import read_csv
from scrolly.io.import_zip import read_zip
from scrolly.io.importers import is_archive, parse_archive, parse_upload

TITLE = 'A "quoted", title\n日落'
TABLE = Table(("id", "title"), [{"id": "1", "title": TITLE}, {"id": "2", "title": None}])


def test_a_backup_zip_reads_back_exactly_and_replaces() -> None:
    archive = read_zip(export_zip({"trial": TABLE, "art": Table(("id",), [])}))
    assert archive.replaces
    assert archive.tables["trial"].rows[0]["title"] == TITLE
    assert archive.tables["trial"].columns == ("id", "title")
    assert archive.tables["art"].rows == []


def test_a_csv_adds_and_is_named_by_its_file() -> None:
    archive = read_csv(table_csv(TABLE), "trial")
    assert not archive.replaces and list(archive.tables) == ["trial"]
    assert len(archive.tables["trial"].rows) == 2


def test_a_zip_with_no_csv_files_is_refused() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("notes.txt", "hello")
    with pytest.raises(ArchiveError, match="no CSV"):
        read_zip(buffer.getvalue())


def test_a_file_that_is_not_a_zip_is_refused() -> None:
    with pytest.raises(ArchiveError, match="not a zip"):
        read_zip(b"hello")


def test_a_csv_without_a_header_is_refused() -> None:
    with pytest.raises(ArchiveError, match="header"):
        read_csv("", "trial")


def test_upload_dispatch_by_file_type() -> None:
    assert is_archive("scrolly-1.zip") and is_archive("Trial.CSV")
    assert not is_archive("backup.json") and not is_archive("dispatch.md")
    assert parse_archive("scrolly-1.zip", export_zip({"art": Table(("id",), [])})).replaces
    assert not parse_archive("trial.csv", b"id,title\n1,A\n").replaces
    with pytest.raises(ImportFormatError, match=r"\.zip"):
        parse_upload("notes.txt", b"hello")
