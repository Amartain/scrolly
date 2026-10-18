from dataclasses import dataclass
from datetime import date

from scrolly.domain.models import Art, ArtKind, HorizonItem, PlanStatus, Trial, TrialState
from scrolly.domain.planning import planning_status
from scrolly.ports import Store

_ON_SCROLL = {TrialState.IMMEDIATE: 0, TrialState.REMAINING: 1}


@dataclass(frozen=True)
class PlanningView:
    status: PlanStatus
    text: str
    trials: list[Trial]
    horizon: list[HorizonItem]
    foundational: list[Art]
    restorative: list[Art]


def build_planning_view(store: Store, today: date) -> PlanningView:
    draft = store.drafts.get()
    on_scroll = sorted(
        (t for t in store.trials.list_for_day(today) if t.state in _ON_SCROLL),
        key=lambda t: (_ON_SCROLL[t.state], t.position),
    )
    arts = store.arts.list_all()
    return PlanningView(
        status=planning_status(store.days.get(today), draft),
        text=draft.text if draft else "",
        trials=on_scroll,
        horizon=store.horizon.list_all(),
        foundational=[a for a in arts if a.kind is ArtKind.FOUNDATIONAL],
        restorative=[a for a in arts if a.kind is ArtKind.RESTORATIVE],
    )
