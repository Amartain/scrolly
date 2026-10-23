"""The player: accepting the Arise window, and choosing the aura."""

from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.player import AuraIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.player import PlayerService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/player")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.post("/accept")
def accept(store: StoreDep, clock: ClockDep) -> ViewOut:
    """[ Yes ] on the Arise window: a player for good; the first time, the System's reward."""
    PlayerService(store, clock.now()).accept()
    return ViewOut.from_data(build_view(store, clock))


@router.put("/aura")
def choose_aura(body: AuraIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    PlayerService(store, clock.now()).choose_aura(body.robe, body.glow, body.glow_on)
    return ViewOut.from_data(build_view(store, clock))
