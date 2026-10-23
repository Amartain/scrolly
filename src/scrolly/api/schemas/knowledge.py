from pydantic import BaseModel

from scrolly.services.knowledge import KnowledgeView


class KnowledgeOut(BaseModel):
    """Knowledge of the Dao. `pending_steps`: the walkthrough's cards still to show, in order (none
    while the tour is off); `complete`: all learned; `enlightened`: and the ceremony was seen."""

    learned: list[str]
    count: int
    total: int
    pending_steps: list[str]
    tour: bool
    bar_hidden: bool
    complete: bool
    enlightened: bool

    @classmethod
    def from_view(cls, view: KnowledgeView) -> "KnowledgeOut":
        return cls(
            learned=view.learned,
            count=view.count,
            total=view.total,
            pending_steps=view.pending_steps,
            tour=view.tour,
            bar_hidden=view.bar_hidden,
            complete=view.complete,
            enlightened=view.enlightened,
        )


class LearnIn(BaseModel):
    key: str


class KnowledgeIn(BaseModel):
    """Only what is given changes."""

    tour: bool | None = None
    bar_hidden: bool | None = None
