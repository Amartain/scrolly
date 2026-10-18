from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.imports import ImportOut
from scrolly.io.errors import ImportFormatError
from scrolly.io.importers import parse_upload
from scrolly.ports import Clock, Store
from scrolly.services.importing import ImportService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.post("/import")
def import_file(file: UploadFile, store: StoreDep, clock: ClockDep) -> ImportOut:
    try:
        batch = parse_upload(file.filename or "", file.file.read())
    except ImportFormatError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    summary = ImportService(store, clock).merge(batch)
    return ImportOut.from_data(summary, build_view(store, clock))
