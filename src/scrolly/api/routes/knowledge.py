"""Knowledge of the Dao: the tour's lessons learned, and the user's choices about it."""

from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.knowledge import KnowledgeIn, KnowledgeOut, LearnIn
from scrolly.api.schemas.view import ViewOut
from scrolly.ports import Clock, Store
from scrolly.services.knowledge import KnowledgeService, build_knowledge
from scrolly.services.view import build_view

router = APIRouter(prefix="/api/knowledge")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


def _service(store: Store, clock: Clock) -> KnowledgeService:
    return KnowledgeService(store, clock.now())


def _view(store: Store, clock: Clock) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.post("/learn")
def learn(body: LearnIn, store: StoreDep, clock: ClockDep) -> KnowledgeOut:
    """A lesson was tried: a step done, or a feature used for the first time.

    Only the knowledge comes back: the click that taught it also did something else, and that
    answer must not be overtaken by an older picture of the whole view."""
    _service(store, clock).learn(body.key)
    return KnowledgeOut.from_view(build_knowledge(store))


@router.post("/pass")
def pass_step(body: LearnIn, store: StoreDep, clock: ClockDep) -> KnowledgeOut:
    """Got it, on a step card: the card goes; doing the thing later still counts."""
    _service(store, clock).pass_step(body.key)
    return KnowledgeOut.from_view(build_knowledge(store))


@router.put("")
def choose(body: KnowledgeIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    _service(store, clock).choose(body.tour, body.bar_hidden)
    return _view(store, clock)


@router.post("/walk-again")
def walk_again(store: StoreDep, clock: ClockDep) -> ViewOut:
    """The step cards show again; nothing learned is lost."""
    _service(store, clock).walk_again()
    return _view(store, clock)


@router.post("/enlightened")
def enlightened(store: StoreDep, clock: ClockDep) -> ViewOut:
    """The Enlightenment ceremony was seen."""
    _service(store, clock).enlightened()
    return _view(store, clock)
