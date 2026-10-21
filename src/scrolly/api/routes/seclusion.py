from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.parallel import CandidateOut, ParallelFinishIn, ParallelPickIn
from scrolly.api.schemas.seclusion import (
    CyclesPlanIn,
    DisciplineIn,
    FinishIn,
    RatioIn,
    SeclusionOut,
)
from scrolly.domain.cycles import make_plan
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


@router.post("/discipline")
def choose_discipline(body: DisciplineIn, seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.switch(body.discipline)
    return SeclusionOut.from_view(seclusion.view())


@router.post("/timer/start")
def start_timer(seclusion: SeclusionDep, body: CyclesPlanIn | None = None) -> SeclusionOut:
    """Start or carry on. On the Cycles dial the body holds what was set; elsewhere it is empty."""
    plan = None if body is None else make_plan(body.focus_min, body.break_min, body.cycles)
    seclusion.start(plan)
    return SeclusionOut.from_view(seclusion.view())


@router.post("/break/start")
def start_break(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.take_break()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/break/end")
def end_break(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.end_break()
    return SeclusionOut.from_view(seclusion.view())


@router.put("/flow/ratio")
def set_ratio(body: RatioIn, seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.set_ratio(body.work, body.rest)
    return SeclusionOut.from_view(seclusion.view())


@router.post("/finish")
def finish(body: FinishIn, seclusion: SeclusionDep) -> SeclusionOut:
    """Conquer, abandon or postpone the trial at hand, with the room's run kept right."""
    seclusion.finish(body.how, body.trial_id)
    return SeclusionOut.from_view(seclusion.view())


@router.get("/parallel/search")
def search_parallel(q: str, seclusion: SeclusionDep) -> list[CandidateOut]:
    """What could run beside the trial at hand: waiting trials, Arts and the Horizon."""
    return [CandidateOut.from_candidate(c) for c in seclusion.parallel.search(q)]


@router.post("/parallel")
def pick_parallel(body: ParallelPickIn, seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.parallel.pick(body.source, body.ref)
    return SeclusionOut.from_view(seclusion.view())


@router.post("/parallel/start")
def start_parallel(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.parallel.start()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/parallel/pause")
def pause_parallel(seclusion: SeclusionDep) -> SeclusionOut:
    seclusion.parallel.pause()
    return SeclusionOut.from_view(seclusion.view())


@router.post("/parallel/finish")
def finish_parallel(body: ParallelFinishIn, seclusion: SeclusionDep) -> SeclusionOut:
    """Conquer, abandon or postpone the parallel trial on its own; the main trial is untouched."""
    seclusion.parallel.finish(body.how)
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
