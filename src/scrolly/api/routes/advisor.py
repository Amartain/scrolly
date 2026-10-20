from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import AdvisorIn, ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.advisor import AdvisorService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/advisor")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.put("")
def silence(body: AdvisorIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    """Not again today (`silenced` true), or let the advisor speak again (false)."""
    AdvisorService(store, clock).silence(body.silenced)
    return ViewOut.from_data(build_view(store, clock))


@router.post("/postpone-mandates")
def postpone_mandates(store: StoreDep, clock: ClockDep) -> ViewOut:
    AdvisorService(store, clock).postpone_mandates()
    return ViewOut.from_data(build_view(store, clock))
