from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.budget import QiCardOut
from scrolly.api.schemas.dashboard import ActualIn, QiActualIn, ScribeIn, TrialPatchIn
from scrolly.api.schemas.planning import OrderIn, SummonIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.day import DayService
from scrolly.services.finished_trials import FinishedTrials
from scrolly.services.qi_card import build_qi_card
from scrolly.services.today import TodayService
from scrolly.services.victory import VictoryService
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/trials")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def get_today(store: StoreDep, clock: ClockDep) -> TodayService:
    DayService(store, clock).ensure_today()
    return TodayService(store, clock)


TodayDep = Annotated[TodayService, Depends(get_today)]


def get_finished(store: StoreDep, clock: ClockDep) -> FinishedTrials:
    DayService(store, clock).ensure_today()
    return FinishedTrials(store, clock)


FinishedDep = Annotated[FinishedTrials, Depends(get_finished)]


def _view(store: Store, clock: Clock) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.post("")
def scribe(body: ScribeIn, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.scribe(body.title, body.estimate, body.qi)
    return _view(store, clock)


@router.post("/summon")
def summon(body: SummonIn, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.summon(body.source, body.id)
    return _view(store, clock)


@router.put("/order")
def reorder(body: OrderIn, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.reorder(body.ids)
    return _view(store, clock)


@router.post("/{trial_id}/promote")
def promote(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.promote(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/timer/start")
def start_timer(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.start_timer(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/timer/pause")
def pause_timer(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.pause_timer(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/timer/reset")
def reset_timer(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.reset_timer(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/conquer")
def conquer(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.conquer(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/postpone")
def postpone(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.postpone(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/abandon")
def abandon(trial_id: str, today: TodayDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    today.abandon(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/revive")
def revive(trial_id: str, finished: FinishedDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    finished.revive(trial_id)
    return _view(store, clock)


@router.post("/{trial_id}/resummon")
def resummon(trial_id: str, finished: FinishedDep, store: StoreDep, clock: ClockDep) -> ViewOut:
    """A double-click on a trial postponed or let go today brings it back."""
    finished.resummon(trial_id)
    return _view(store, clock)


@router.put("/{trial_id}/qi")
def set_qi(
    trial_id: str, body: QiActualIn, finished: FinishedDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    """The Qi a conquered trial took. Until it is told, the estimate stands."""
    finished.set_actual_qi(trial_id, body.qi)
    return _view(store, clock)


@router.get("/{trial_id}/qi-card")
def qi_card(trial_id: str, qi: int, store: StoreDep, clock: ClockDep) -> QiCardOut:
    """The card after a conquest: its choices, and the day's Qi if `qi` were the answer."""
    return QiCardOut.from_view(build_qi_card(store, clock.now(), trial_id, qi))


@router.put("/{trial_id}/actual")
def set_actual(
    trial_id: str, body: ActualIn, finished: FinishedDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    """The time a conquered trial really took, as the user corrects it."""
    finished.set_actual(trial_id, body.text)
    return _view(store, clock)


@router.patch("/{trial_id}")
def update(
    trial_id: str, body: TrialPatchIn, today: TodayDep, store: StoreDep, clock: ClockDep
) -> ViewOut:
    today.update(trial_id, **body.model_dump())
    return _view(store, clock)


@router.post("/victory-seen")
def victory_seen(store: StoreDep, clock: ClockDep) -> ViewOut:
    """Tribulation Weathered was read and closed (Sheathe the Sword)."""
    VictoryService(store, clock).settle()
    return _view(store, clock)
