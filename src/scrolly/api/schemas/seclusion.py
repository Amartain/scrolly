from pydantic import BaseModel

from scrolly.api.schemas.dashboard import ImmediateOut
from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.models import Trial
from scrolly.domain.seclusion import IncenseState, IncenseView
from scrolly.domain.segments import Discipline
from scrolly.services.seclusion import SeclusionView


class IncenseOut(BaseModel):
    state: IncenseState
    remaining_s: int
    over_s: int

    @classmethod
    def from_view(cls, view: IncenseView) -> "IncenseOut":
        return cls(state=view.state, remaining_s=view.remaining_s, over_s=view.over_s)


class WaitingOut(BaseModel):
    """A trial that waits in Remaining: enough to choose it in "Switch trials"."""

    id: str
    title: str
    type: TrialType

    @classmethod
    def from_trial(cls, trial: Trial) -> "WaitingOut":
        return cls(id=trial.id, title=trial.title, type=type_of(trial.is_mandate, trial.art_kind))


class SeclusionOut(BaseModel):
    active: bool
    discipline: Discipline
    trial: ImmediateOut | None
    note: str
    ring_elapsed_s: int
    incense: IncenseOut | None
    gong_in_s: int | None
    remaining: list[WaitingOut]

    @classmethod
    def from_view(cls, view: SeclusionView) -> "SeclusionOut":
        trial = None
        if view.trial is not None and view.timer is not None:
            trial = ImmediateOut.from_trial(view.trial, view.timer)
        return cls(
            active=view.active,
            discipline=view.discipline,
            trial=trial,
            note="" if view.trial is None else view.trial.note,
            ring_elapsed_s=view.ring_elapsed_s,
            incense=None if view.incense is None else IncenseOut.from_view(view.incense),
            gong_in_s=view.gong_in_s,
            remaining=[WaitingOut.from_trial(t) for t in view.remaining],
        )
