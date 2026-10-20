"""Keeping a copy of the data before a restore replaces it."""

from collections.abc import Callable
from pathlib import Path

from scrolly.domain.archive import Tables
from scrolly.io.export_csv import export_zip


def copy_keeper(folder: Path | None, stamp: str) -> Callable[[Tables], None]:
    """A function that saves the given tables as a Backup Scroll zip in `folder`."""

    def keep(tables: Tables) -> None:
        if folder is None:
            return
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"scrolly-before-restore-{stamp}.zip").write_bytes(export_zip(tables))

    return keep
