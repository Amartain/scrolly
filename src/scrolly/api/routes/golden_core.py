from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.planning import GoldenCoreIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.golden_core import GoldenCoreService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/golden-core")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.put("")
def set_enabled(body: GoldenCoreIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    """Awaken or put away the Golden Core. Either answer retires the invitation."""
    GoldenCoreService(store, clock).set_enabled(body.enabled)
    return ViewOut.from_data(build_view(store, clock))
