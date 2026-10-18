from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import AppearanceIn, HealthOut, ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.appearance import AppearanceService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.get("/health")
def health() -> HealthOut:
    return HealthOut()


@router.get("/view")
def view(store: StoreDep, clock: ClockDep) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.put("/appearance")
def choose_appearance(body: AppearanceIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    AppearanceService(store, clock).choose(body.theme, body.day_variant)
    return ViewOut.from_data(build_view(store, clock))
