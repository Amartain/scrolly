from scrolly.clock import FixedClock
from scrolly.domain.models import PlanStatus
from scrolly.ports import Store
from scrolly.services.planning import PlanningService
from scrolly.services.planning_trials import PlanningTrialsService
from scrolly.services.planning_view import build_planning_view
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
