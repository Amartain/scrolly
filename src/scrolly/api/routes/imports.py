from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile

from scrolly.api.backup import copy_keeper
from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.imports import ImportOut
from scrolly.api.schemas.view import ViewOut
from scrolly.io.errors import ImportFormatError
from scrolly.io.export_csv import backup_name
from scrolly.io.importers import is_archive, parse_archive, parse_upload
from scrolly.ports import Clock, Store
from scrolly.services.archive import ArchiveService
from scrolly.services.importing import ImportService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.post("/import")
def import_file(file: UploadFile, request: Request, store: StoreDep, clock: ClockDep) -> ImportOut:
    name, content = file.filename or "", file.file.read()
    if is_archive(name):
        # A zip or CSV is read as whole tables; a bad one is refused (422) before anything changes.
        archive = parse_archive(name, content)
        stamp = backup_name(clock.now()).removeprefix("scrolly-").removesuffix(".zip")
        keeper = copy_keeper(request.app.state.backup_dir, stamp)
        added, skipped = ArchiveService(store, clock, keeper).restore(archive)
        return ImportOut.from_counts(added, skipped, ViewOut.from_data(build_view(store, clock)))
    try:
        batch = parse_upload(name, content)
    except ImportFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    summary = ImportService(store, clock).merge(batch)
    return ImportOut.from_data(summary, build_view(store, clock))


@router.post("/purge")
def purge_today(store: StoreDep, clock: ClockDep) -> ViewOut:
    """Purge Today's Scroll: today's open trials and the planning in progress."""
    ArchiveService(store, clock).purge_today()
    return ViewOut.from_data(build_view(store, clock))
