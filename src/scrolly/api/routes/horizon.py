from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.horizon import ArtOrderIn, HorizonAddIn, HorizonPatchIn
from scrolly.api.schemas.planning import OrderIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.horizon import HorizonService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def get_horizon(store: StoreDep, clock: ClockDep) -> HorizonService:
    DayService(store, clock).ensure_today()
    return HorizonService(store, clock)


HorizonDep = Annotated[HorizonService, Depends(get_horizon)]


def _view(store: Store, clock: Clock) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.post("/horizon")
def add(body: HorizonAddIn, horizon: HorizonDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    horizon.add(body.title)
    return _view(store, clock)


@router.put("/horizon/order")
def reorder(body: OrderIn, horizon: HorizonDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    horizon.reorder(body.ids)
    return _view(store, clock)


@router.patch("/horizon/{item_id}")
def edit(
    item_id: str, body: HorizonPatchIn, horizon: HorizonDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    horizon.edit(item_id, **body.model_dump())
    return _view(store, clock)


@router.delete("/horizon/{item_id}")
def discard(item_id: str, horizon: HorizonDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    horizon.discard(item_id)
    return _view(store, clock)


@router.put("/arts/order")
def reorder_arts(
    body: ArtOrderIn, horizon: HorizonDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    horizon.reorder_arts(body.kind, body.ids)
    return _view(store, clock)
