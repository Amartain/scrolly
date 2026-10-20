from collections.abc import Callable
from pathlib import PurePath

from scrolly.domain.archive import Archive
from scrolly.domain.merge import ImportBatch
from scrolly.io.errors import ImportFormatError
from scrolly.io.import_csv import read_csv
from scrolly.io.import_discord_md import parse_discord_md
from scrolly.io.import_prototype_json import parse_prototype_json
from scrolly.io.import_zip import read_zip

# Text formats that merge into the data: an old Scrolly backup and a Discord Dispatch.
PARSERS: dict[str, Callable[[str, str], ImportBatch]] = {
    ".json": parse_prototype_json,
    ".md": parse_discord_md,
}

ARCHIVE_SUFFIXES = {".zip", ".csv"}

HINT = (
    "Restore reads a Scrolly backup (.zip), a table (.csv), an old backup (.json) or Discord (.md)"
)


def is_archive(filename: str) -> bool:
    """Whole tables (a Backup Scroll zip, or one table as CSV) rather than a merge batch."""
    return PurePath(filename).suffix.lower() in ARCHIVE_SUFFIXES


def _text(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ImportFormatError("This file is not UTF-8 text") from error


def parse_archive(filename: str, content: bytes) -> Archive:
    """A zip replaces the data; a CSV (named after its table) adds the rows that are new."""
    path = PurePath(filename)
    if path.suffix.lower() == ".zip":
        return read_zip(content)
    return read_csv(_text(content), path.stem)


def parse_upload(filename: str, content: bytes) -> ImportBatch:
    path = PurePath(filename)
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ImportFormatError(HINT)
    return parser(_text(content), path.stem)
