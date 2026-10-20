from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.dispatch import DispatchIn, DispatchOut, SymbolIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.dispatch import DispatchService, build_dispatch, load_options
from scrolly.services.legend import LegendService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def _dispatch(store: Store, clock: Clock) -> DispatchOut:
    DayService(store, clock).ensure_today()
    return DispatchOut.build(build_dispatch(store, clock.now()), load_options(store))


@router.get("/dispatch")
def dispatch(store: StoreDep, clock: ClockDep) -> DispatchOut:
    return _dispatch(store, clock)


@router.put("/dispatch")
def choose_dispatch(body: DispatchIn, store: StoreDep, clock: ClockDep) -> DispatchOut:
    DispatchService(store, clock).choose(body.dnd, body.include_postponed, body.include_abandoned)
    return _dispatch(store, clock)


@router.put("/legend")
def choose_symbol(body: SymbolIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    LegendService(store, clock).set_symbol(body.group, body.key, body.emoji, body.shortcode)
    return ViewOut.from_data(build_view(store, clock))
