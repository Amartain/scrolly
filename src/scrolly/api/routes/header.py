from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import Response

from scrolly.api.deps import get_clock, get_store
from scrolly.api.header_file import HeaderFile
from scrolly.api.schemas.view import HeaderIn, ViewOut
from scrolly.domain.header_image import sniff_image
from scrolly.ports import Clock, Store
from scrolly.services.appearance import AppearanceService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def _file(request: Request) -> HeaderFile:
    return HeaderFile(request.app.state.data_dir)


@router.put("/header")
def choose_header(body: HeaderIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    AppearanceService(store, clock).choose_header(body.choice)
    return ViewOut.from_data(build_view(store, clock))


@router.post("/header-image")
def upload_header_image(
    file: UploadFile, request: Request, store: StoreDep, clock: ClockDep
) -> ViewOut:
    """The user's own picture for the header band: PNG, JPEG or WebP, up to 5 MB."""
    content = file.file.read()
    _file(request).save(content, sniff_image(content))
    AppearanceService(store, clock).use_uploaded_header()
    return ViewOut.from_data(build_view(store, clock))


@router.get("/header-image")
def header_image(request: Request) -> Response:
    found = _file(request).read()
    if found is None:
        raise HTTPException(status_code=404, detail="No picture of your own yet")
    content, media_type = found
    return Response(content, media_type=media_type)
