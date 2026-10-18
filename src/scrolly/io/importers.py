from collections.abc import Callable
from pathlib import PurePath

from scrolly.domain.merge import ImportBatch
from scrolly.io.errors import ImportFormatError
from scrolly.io.import_discord_md import parse_discord_md
from scrolly.io.import_prototype_json import parse_prototype_json

# Zip and CSV importers join this dict in build step 7.
PARSERS: dict[str, Callable[[str, str], ImportBatch]] = {
    ".json": parse_prototype_json,
    ".md": parse_discord_md,
}


def parse_upload(filename: str, content: bytes) -> ImportBatch:
    path = PurePath(filename)
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ImportFormatError("Restore reads .json (old Scrolly backup) and .md (Discord) files")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ImportFormatError("This file is not UTF-8 text") from error
    return parser(text, path.stem)
