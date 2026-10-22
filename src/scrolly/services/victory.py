from dataclasses import dataclass, replace
from datetime import date, datetime

from scrolly.domain.day_flow import is_victory
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day, Trial
from scrolly.domain.victory import (
    Scene,
    VictoryTally,
    victory_due,
    victory_line,
    victory_scene,
    victory_tally,
)
from scrolly.ports import Clock, Store
from scrolly.services.victory_content import load_victory_lines


@dataclass(frozen=True)
class VictoryView:
    """The finished-day ceremony: the scene, the day's tally and line. `due`: still owed."""

    scene: Scene
    tally: VictoryTally
    line: str
    due: bool


def build_victory(day: Day | None, trials: list[Trial], today: date) -> VictoryView | None:
    if not is_victory(day, trials):
        return None
    return VictoryView(
        scene=victory_scene(trials),
        tally=victory_tally(trials),
        line=victory_line(today, load_victory_lines()),
        due=victory_due(day, trials),
    )


def build_preview(store: Store, now: datetime, scene: Scene) -> VictoryView:
    """The ceremony a secret seal asks for: today's tally as it stands, won or not, in the scene
    asked for. Nothing is stored."""
    today = logical_day(now)
    trials = store.trials.list_for_day(today)
    return VictoryView(
        scene=scene,
        tally=victory_tally(trials),
        line=victory_line(today, load_victory_lines()),
        due=True,
    )


class VictoryService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def settle(self) -> None:
        """The ceremony was closed: it does not come again until another trial is conquered."""
        now: datetime = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        self._store.days.save(replace(day, victory_seen_at=now), now)
