from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.seclusion import SeclusionOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.seclusion import SeclusionService

router = APIRouter(prefix="/api/seclusion")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def get_seclusion(store: StoreDep, clock: ClockDep) -> SeclusionService:
    DayService(store, clock).ensure_today()
    return SeclusionService(store, clock)


SeclusionDep = Annotated[SeclusionService, Depends(get_seclusion)]


@router.get("")
def get_state(seclusion: SeclusionDep) -> SeclusionOut:
    return SeclusionOut.from_view(seclusion.view())


@router.post("/enter")
def enter(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.enter()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/leave")
def leave(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.leave()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/timer/start")
def start_timer(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.start()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/timer/pause")
def pause_timer(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.pause()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/timer/new")
def new_timer(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.new_timer()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/timer/zero")
def zero_out(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.zero_out()
    return SeclusionOut.from_view(seclusion.view())
