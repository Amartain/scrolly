from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.horizon import ArtAddIn, ArtPatchIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.arts import ArtsService
from scrolly.services.day import DayService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/arts")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def get_arts(store: StoreDep, clock: ClockDep) -> ArtsService:
    DayService(store, clock).ensure_today()
    return ArtsService(store, clock)


ArtsDep = Annotated[ArtsService, Depends(get_arts)]


def _view(store: Store, clock: Clock) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.post("")
def add(body: ArtAddIn, arts: ArtsDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    arts.add(body.kind, body.title, body.estimate)
    return _view(store, clock)


@router.patch("/{art_id}")
def edit(art_id: str, body: ArtPatchIn, arts: ArtsDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    arts.edit(art_id, body.title, body.estimate)
    return _view(store, clock)


@router.delete("/{art_id}")
def remove(art_id: str, arts: ArtsDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    arts.remove(art_id)
    return _view(store, clock)
