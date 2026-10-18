from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.planning import OrderIn, SummonIn, TextIn, TrialIn, TrialPatchIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.planning import PlanningService
from scrolly.services.planning_trials import PlanningTrialsService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/planning")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def get_planning(store: StoreDep, clock: ClockDep) -> PlanningService:
    DayService(store, clock).ensure_today()
    return PlanningService(store, clock)


def get_scroll(store: StoreDep, clock: ClockDep) -> PlanningTrialsService:
    DayService(store, clock).ensure_today()
    return PlanningTrialsService(store, clock)


PlanningDep = Annotated[PlanningService, Depends(get_planning)]
ScrollDep = Annotated[PlanningTrialsService, Depends(get_scroll)]


def _view(store: Store, clock: Clock) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.post("/start")
def start(planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.start()
    return _view(store, clock)


@router.put("/text")
def save_text(body: TextIn, planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.save_text(body.text)
    return _view(store, clock)


@router.post("/proceed")
def proceed(planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.proceed()
    return _view(store, clock)


@router.post("/back")
def back(planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.back()
    return _view(store, clock)


@router.post("/abandon")
def abandon(planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.abandon()
    return _view(store, clock)


@router.post("/seal")
def seal(planning: PlanningDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    planning.seal()
    return _view(store, clock)


@router.post("/summon")
def summon(body: SummonIn, scroll: ScrollDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    scroll.summon(body.source, body.id)
    return _view(store, clock)


@router.post("/trials")
def add_trial(body: TrialIn, scroll: ScrollDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    scroll.add(body.title)
    return _view(store, clock)


@router.patch("/trials/{trial_id}")
def update_trial(
    trial_id: str, body: TrialPatchIn, scroll: ScrollDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    scroll.update(trial_id, body.estimate, body.is_mandate)
    return _view(store, clock)


@router.post("/trials/{trial_id}/unstage")
def unstage(trial_id: str, scroll: ScrollDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    scroll.unstage(trial_id)
    return _view(store, clock)


@router.post("/trials/{trial_id}/dismiss")
def dismiss(trial_id: str, scroll: ScrollDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    scroll.dismiss(trial_id)
    return _view(store, clock)


@router.put("/order")
def reorder(body: OrderIn, scroll: ScrollDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    scroll.reorder(body.ids)
    return _view(store, clock)
