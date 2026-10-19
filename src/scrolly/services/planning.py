import uuid
from dataclasses import replace
from datetime import date, datetime

from scrolly.domain.art_match import art_kind_for
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day, PlanningDraft, PlanPhase, Trial, TrialState
from scrolly.domain.planning import (
    PlanningError,
    abandon,
    dump_lines,
    next_position,
    seal,
    trial_from_line,
)
from scrolly.domain.qi import choose_start
from scrolly.domain.uniqueness import require_free_dump
from scrolly.ports import Clock, Store
from scrolly.services.golden_core import chosen_start, read_setting, todays_outlook


def abandon_planning(store: Store, draft: PlanningDraft, now: datetime) -> None:
    """Drop an unsealed scroll and give the Horizon back what it lent. A sealed day is kept."""
    day = store.days.get(draft.logical_day)
    if day is None or day.first_sealed_at is None:
        trials = store.trials.list_for_day(draft.logical_day)
        store.horizon.replace_all(abandon(trials, store.horizon.list_all()), now)
        store.trials.delete([t.id for t in trials])
    store.drafts.delete()


def planning_trials(store: Store, today: date) -> list[Trial]:
    """What is on today's scroll while planning, in order."""
    waiting = [t for t in store.trials.list_for_day(today) if t.state is TrialState.REMAINING]
    return sorted(waiting, key=lambda t: t.position)


class PlanningService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    @property
    def _today(self) -> date:
        return logical_day(self._now)

    def _draft(self, *phases: PlanPhase) -> PlanningDraft:
        draft = self._store.drafts.get()
        if draft is None or draft.phase not in phases:
            raise PlanningError("That step is not open right now")
        return draft

    def _golden_core_on(self) -> bool:
        return read_setting(self._store).enabled

    def start(self) -> None:
        if self._store.drafts.get() is None:
            self._store.drafts.save(PlanningDraft(logical_day=self._today), self._now)

    def save_text(self, text: str) -> None:
        draft = self._draft(PlanPhase.INSCRIBE)
        self._store.drafts.save(replace(draft, text=text), self._now)

    def proceed(self) -> None:
        """Inscribe -> Estimate, and with the Golden Core on, Estimate -> Weigh the Qi."""
        draft = self._draft(PlanPhase.INSCRIBE, PlanPhase.ESTIMATE)
        if draft.phase is PlanPhase.ESTIMATE:
            self._weigh(draft)
        else:
            self._estimate(draft)

    def _weigh(self, draft: PlanningDraft) -> None:
        if not self._golden_core_on():
            raise PlanningError("The Golden Core is not awakened")
        self._store.drafts.save(replace(draft, phase=PlanPhase.WEIGH), self._now)

    def _estimate(self, draft: PlanningDraft) -> None:
        scroll = planning_trials(self._store, self._today)
        lines = dump_lines(draft.text)
        if not lines and not scroll:
            raise PlanningError("Scribe or summon at least one trial first")
        arts = self._store.arts.list_all()
        require_free_dump(
            lines,
            self._store.horizon.list_all(),
            self._store.trials.list_for_day(self._today),
            arts,
        )
        position = next_position(scroll)
        added = [
            trial_from_line(
                str(uuid.uuid4()), line, self._today, position + i, art_kind_for(line, arts)
            )
            for i, line in enumerate(lines)
        ]
        self._store.trials.save(added, self._now)
        self._store.drafts.save(replace(draft, phase=PlanPhase.ESTIMATE, text=""), self._now)

    def back(self) -> None:
        draft = self._draft(PlanPhase.ESTIMATE, PlanPhase.WEIGH)
        earlier = PlanPhase.INSCRIBE if draft.phase is PlanPhase.ESTIMATE else PlanPhase.ESTIMATE
        self._store.drafts.save(replace(draft, phase=earlier), self._now)

    def set_qi_start(self, value: int) -> None:
        draft = self._draft(PlanPhase.WEIGH)
        available = todays_outlook(self._store, self._today)
        self._store.drafts.save(replace(draft, qi_start=choose_start(value, available)), self._now)

    def abandon(self) -> None:
        draft = self._store.drafts.get()
        if draft is not None:
            abandon_planning(self._store, draft, self._now)

    def seal(self) -> None:
        draft = self._draft(PlanPhase.ESTIMATE, PlanPhase.WEIGH)
        qi_start = None
        if self._golden_core_on():
            if draft.phase is PlanPhase.ESTIMATE:
                raise PlanningError("Weigh the Qi before sealing the scroll")
            qi_start = chosen_start(self._store, draft, self._today)
        now = self._now
        day = self._store.days.get(self._today) or Day(logical_day=self._today)
        first, sealed_day = seal(planning_trials(self._store, self._today), day, now, qi_start)
        self._store.trials.save([first], now)
        self._store.days.save(sealed_day, now)
        self._store.drafts.delete()
