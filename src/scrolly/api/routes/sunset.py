from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import SunsetIn, ViewOut
from scrolly.domain.sunset import SunsetError
from scrolly.ports import Clock, Store
from scrolly.services.poem import PoemService
from scrolly.services.sunset import SunsetService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.put("/sunset")
def choose_sunset(body: SunsetIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    """Answer the invitation, or change the sunset hour, the on/off choice or the chime."""
    try:
        SunsetService(store, clock).choose(body.enabled, body.at, body.chime)
    except SunsetError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ViewOut.from_data(build_view(store, clock))


@router.post("/sunset/poem-seen")
def poem_seen(store: StoreDep, clock: ClockDep) -> ViewOut:
    """The sunset poem was read and closed ("Settle Qi")."""
    PoemService(store, clock).settle()
    return ViewOut.from_data(build_view(store, clock))
