import uuid
from dataclasses import replace
from datetime import date, datetime

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
from scrolly.ports import Clock, Store


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

    def _draft(self, phase: PlanPhase) -> PlanningDraft:
        draft = self._store.drafts.get()
        if draft is None or draft.phase is not phase:
            raise PlanningError("That step is not open right now")
        return draft

    def start(self) -> None:
        if self._store.drafts.get() is None:
            self._store.drafts.save(PlanningDraft(logical_day=self._today), self._now)

    def save_text(self, text: str) -> None:
        draft = self._draft(PlanPhase.INSCRIBE)
        self._store.drafts.save(replace(draft, text=text), self._now)

    def proceed(self) -> None:
        draft = self._draft(PlanPhase.INSCRIBE)
        scroll = planning_trials(self._store, self._today)
        lines = dump_lines(draft.text)
        if not lines and not scroll:
            raise PlanningError("Scribe or summon at least one trial first")
        position = next_position(scroll)
        added = [
            trial_from_line(str(uuid.uuid4()), line, self._today, position + i)
            for i, line in enumerate(lines)
        ]
        self._store.trials.save(added, self._now)
        self._store.drafts.save(replace(draft, phase=PlanPhase.ESTIMATE, text=""), self._now)

    def back(self) -> None:
        draft = self._draft(PlanPhase.ESTIMATE)
        self._store.drafts.save(replace(draft, phase=PlanPhase.INSCRIBE), self._now)

    def abandon(self) -> None:
        draft = self._store.drafts.get()
        if draft is not None:
            abandon_planning(self._store, draft, self._now)

    def seal(self) -> None:
        self._draft(PlanPhase.ESTIMATE)
        now = self._now
        day = self._store.days.get(self._today) or Day(logical_day=self._today)
        first, sealed_day = seal(planning_trials(self._store, self._today), day, now)
        self._store.trials.save([first], now)
        self._store.days.save(sealed_day, now)
        self._store.drafts.delete()
