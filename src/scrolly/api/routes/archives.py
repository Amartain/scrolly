from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.archives import ArchivePageOut
from scrolly.ports import Clock, Store
from scrolly.services.archives_view import build_archives

router = APIRouter(prefix="/api/archives")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.get("")
def archives(store: StoreDep, clock: ClockDep, before: date | None = None) -> ArchivePageOut:
    """The Grand Archives: fourteen past days, newest first. `before` asks for older ones."""
    return ArchivePageOut.from_page(build_archives(store, clock.now(), before))
