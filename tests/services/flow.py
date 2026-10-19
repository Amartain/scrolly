from scrolly.clock import FixedClock
from scrolly.domain.models import PlanStatus, Trial, TrialState
from scrolly.ports import Store
from scrolly.services.planning import PlanningService
from scrolly.services.planning_trials import PlanningTrialsService
from scrolly.services.planning_view import build_planning_view
from scrolly.services.today import TodayService
from tests.factories import DAY


class Flow:
    """The services a request would build, sharing one store and clock."""

    def __init__(self, store: Store, clock: FixedClock) -> None:
        self.store, self.clock = store, clock
        self.planning = PlanningService(store, clock)
        self.scroll = PlanningTrialsService(store, clock)

    def status(self) -> PlanStatus:
        return build_planning_view(self.store, DAY).status

    def titles(self) -> list[str]:
        return [t.title for t in build_planning_view(self.store, DAY).trials]


def seal_day(store: Store, clock: FixedClock, *titles: str) -> TodayService:
    """Plan and seal a day with one trial per title; the first becomes the Immediate Trial."""
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("\n".join(titles))
    flow.planning.proceed()
    flow.planning.seal()
    return TodayService(store, clock)


def by_title(store: Store) -> dict[str, Trial]:
    return {t.title: t for t in store.trials.list_for_day(DAY)}


def states(store: Store) -> dict[str, TrialState]:
    return {title: t.state for title, t in by_title(store).items()}
