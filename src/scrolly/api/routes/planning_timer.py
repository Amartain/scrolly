from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.planning_timer import PlanningTimerService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/planning/timer")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def _timer(store: Store, clock: Clock) -> PlanningTimerService:
    DayService(store, clock).ensure_today()
    return PlanningTimerService(store, clock)


@router.post("/start")
def start(store: StoreDep, clock: ClockDep) -> ViewOut:
    _timer(store, clock).start()
    return ViewOut.from_data(build_view(store, clock))


@router.post("/pause")
def pause(store: StoreDep, clock: ClockDep) -> ViewOut:
    _timer(store, clock).pause()
    return ViewOut.from_data(build_view(store, clock))


@router.post("/reset")
def reset(store: StoreDep, clock: ClockDep) -> ViewOut:
    _timer(store, clock).reset()
    return ViewOut.from_data(build_view(store, clock))
