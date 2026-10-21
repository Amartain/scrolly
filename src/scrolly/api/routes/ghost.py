from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.ghost import GhostService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/ghost")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.post("/keep")
def keep(store: StoreDep, clock: ClockDep) -> ViewOut:
    """The time away counts: every timer carries on as if it had never stopped."""
    GhostService(store, clock).keep()
    return ViewOut.from_data(build_view(store, clock))


@router.post("/cut")
def cut(store: StoreDep, clock: ClockDep) -> ViewOut:
    """Count only until the user left."""
    GhostService(store, clock).cut()
    return ViewOut.from_data(build_view(store, clock))
