from typing import Annotated

from fastapi import APIRouter, Depends, Request

from scrolly.api.backup import copy_keeper
from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.dashboard import VictoryOut
from scrolly.api.schemas.milestone import MilestoneOut
from scrolly.api.schemas.seals import SealIn, SealOut
from scrolly.api.schemas.view import ViewOut
from scrolly.domain.secret_seals import SealKind
from scrolly.io.export_csv import backup_name
from scrolly.ports import Clock, Store
from scrolly.services.milestone_content import milestone_after
from scrolly.services.seals import SealService
from scrolly.services.victory import build_preview
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.post("/seal-inscription")
def inscribe(body: SealIn, request: Request, store: StoreDep, clock: ClockDep) -> SealOut:
    """Words typed into Settings, Secret Seal Inscription. Unknown words do nothing."""
    stamp = backup_name(clock.now()).removeprefix("scrolly-").removesuffix(".zip")
    data_dir = request.app.state.data_dir
    folder = None if data_dir is None else data_dir / "backups"
    seal = SealService(store, clock, copy_keeper(folder, stamp, "before-restart")).inscribe(
        body.text
    )
    view = ViewOut.from_data(build_view(store, clock))
    if seal is not None and seal.kind is SealKind.DAY and seal.day is not None:
        view.milestone = MilestoneOut.from_milestone(milestone_after(seal.day))
    preview = None
    if seal is not None and seal.kind is SealKind.CEREMONY and seal.scene is not None:
        preview = VictoryOut.from_view(build_preview(store, clock.now(), seal.scene))
    return SealOut(recognized=seal is not None, view=view, victory_preview=preview)
