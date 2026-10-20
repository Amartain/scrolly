from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from scrolly.api.deps import get_clock, get_store
from scrolly.io.export_csv import backup_name, export_zip
from scrolly.ports import Clock, Store
from scrolly.services.archive import current_tables

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.get("/export")
def export(store: StoreDep, clock: ClockDep) -> Response:
    """Backup Scroll: a timestamped zip with one CSV per table."""
    name = backup_name(clock.now())
    return Response(
        export_zip(current_tables(store)),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )
