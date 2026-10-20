import csv
import io
import zipfile

from scrolly.domain.archive import Table
from scrolly.io.export_csv import export_zip, table_csv


def _rows(content: bytes, name: str) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        text = archive.read(name).decode("utf-8")
    return list(csv.reader(io.StringIO(text)))


def test_each_table_is_a_csv_with_a_header_and_empty_cells_for_missing_values() -> None:
    table = Table(
        ("id", "title", "essence_expected_min"),
        [{"id": "a", "title": "Read", "essence_expected_min": None}],
    )
    assert table_csv(table).splitlines() == ["id,title,essence_expected_min", "a,Read,"]


def test_an_empty_table_still_has_its_header() -> None:
    zipped = export_zip({"art": Table(("id", "kind"), [])})
    assert _rows(zipped, "art.csv") == [["id", "kind"]]


def test_titles_with_commas_quotes_newlines_and_other_scripts_survive() -> None:
    title = 'Write "the, report"\n日落 — café'
    zipped = export_zip({"trial": Table(("id", "title"), [{"id": "1", "title": title}])})
    assert _rows(zipped, "trial.csv")[1] == ["1", title]


def test_the_zip_holds_one_file_per_table() -> None:
    zipped = export_zip({"a": Table(("id",), []), "b": Table(("id",), [])})
    with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
        assert sorted(archive.namelist()) == ["a.csv", "b.csv"]
