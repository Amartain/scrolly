from typing import Literal

from pydantic import BaseModel

from scrolly.api.schemas.budget import BudgetOut, QiOut
from scrolly.domain.day_budget import DayBudget
from scrolly.domain.duration import format_duration
from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.models import Art, HorizonItem, OriginType, PlanStatus, Trial, TrialState
from scrolly.services.golden_core import QiView
from scrolly.services.planning_view import PlanningView


def _estimate(minutes: int | None) -> str:
    return "" if minutes is None else format_duration(minutes)


class PlanTrialOut(BaseModel):
    id: str
    title: str
    state: TrialState
    is_mandate: bool
    origin_type: OriginType
    type: TrialType
    expected_text: str
    qi_text: str

    @classmethod
    def from_trial(cls, trial: Trial) -> "PlanTrialOut":
        return cls(
            id=trial.id,
            title=trial.title,
            state=trial.state,
            is_mandate=trial.is_mandate,
            origin_type=trial.origin_type,
            type=type_of(trial.is_mandate, trial.origin_type),
            expected_text=_estimate(trial.essence_expected_min),
            qi_text="" if trial.qi_expected is None else str(trial.qi_expected),
        )


class HorizonItemOut(BaseModel):
    id: str
    title: str
    is_mandate: bool
    type: TrialType
    expected_text: str

    @classmethod
    def from_item(cls, item: HorizonItem) -> "HorizonItemOut":
        return cls(
            id=item.id,
            title=item.title,
            is_mandate=item.is_mandate,
            type=type_of(item.is_mandate, item.origin_type),
            expected_text=_estimate(item.essence_expected_min),
        )


class ArtOut(BaseModel):
    id: str
    title: str
    expected_text: str

    @classmethod
    def from_art(cls, art: Art) -> "ArtOut":
        return cls(id=art.id, title=art.title, expected_text=_estimate(art.essence_expected_min))


class PlanningOut(BaseModel):
    status: PlanStatus
    text: str
    trials: list[PlanTrialOut]
    horizon: list[HorizonItemOut]
    foundational: list[ArtOut]
    restorative: list[ArtOut]
    budget: BudgetOut
    qi: QiOut

    @classmethod
    def from_data(cls, data: PlanningView, budget: DayBudget, qi: QiView) -> "PlanningOut":
        return cls(
            status=data.status,
            text=data.text,
            trials=[PlanTrialOut.from_trial(t) for t in data.trials],
            horizon=[HorizonItemOut.from_item(i) for i in data.horizon],
            foundational=[ArtOut.from_art(a) for a in data.foundational],
            restorative=[ArtOut.from_art(a) for a in data.restorative],
            budget=BudgetOut.from_budget(budget),
            qi=QiOut.from_view(qi),
        )


class TextIn(BaseModel):
    text: str


class SummonIn(BaseModel):
    source: Literal["horizon", "art"]
    id: str


class TrialIn(BaseModel):
    title: str


class TrialPatchIn(BaseModel):
    """Only the fields that are sent change. An empty estimate clears it."""

    estimate: str | None = None
    is_mandate: bool | None = None
    qi: str | None = None


class QiStartIn(BaseModel):
    value: int


class GoldenCoreIn(BaseModel):
    enabled: bool


class OrderIn(BaseModel):
    ids: list[str]
