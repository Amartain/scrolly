"""Tribulation Weathered: the moment the day's last trial is conquered. Pure, no IO."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from scrolly.domain.day_flow import is_victory
from scrolly.domain.duration import format_duration
from scrolly.domain.models import Day, Trial, TrialState


class Scene(StrEnum):
    """What plays before the card: heavenly lightning, or the wind and the rising sun."""

    THUNDER = "thunder"
    WIND = "wind"


def victory_scene(trials: Sequence[Trial]) -> Scene:
    """A day that conquered a Heavenly Mandate weathered a tribulation: it gets the thunder."""
    mandate = any(t.state is TrialState.DONE and t.is_mandate for t in trials)
    return Scene.THUNDER if mandate else Scene.WIND


@dataclass(frozen=True)
class VictoryTally:
    conquered: int
    mandates: int
    essence_text: str  # the time worked on what was conquered, "5h12m"


def victory_due(day: Day | None, trials: Sequence[Trial]) -> bool:
    """The ceremony is owed: the day is won and no ceremony came after the latest conquest.

    Scribing and conquering one more trial after the user closed it earns the ceremony again.
    """
    if not is_victory(day, trials) or day is None:
        return False
    if day.victory_seen_at is None:
        return True
    latest = max((t.completed_at for t in trials if t.completed_at is not None), default=None)
    return latest is not None and latest > day.victory_seen_at


def victory_tally(trials: Sequence[Trial]) -> VictoryTally:
    done = [t for t in trials if t.state is TrialState.DONE]
    minutes = sum(t.essence_actual_min or 0 for t in done)
    return VictoryTally(
        conquered=len(done),
        mandates=sum(1 for t in done if t.is_mandate),
        essence_text=format_duration(minutes),
    )


def victory_line(day: date, lines: Sequence[str]) -> str:
    """The line of the day. Lines take turns, so a reload shows the same one."""
    return lines[day.toordinal() % len(lines)]
