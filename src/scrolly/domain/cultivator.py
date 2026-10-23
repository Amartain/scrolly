"""Where the cultivator of the peak is: at the foot of the path, or up on the peak. Pure, no IO.

The peak behind Seclusion and in the dashboard header (owner, 2026-10-23). The first focus sends the
cultivator up; there they meditate, and any number of trials can be conquered without them moving.
Pausing and stepping out leave them there too. They come down when the room's Cycles or Flow run
ends (the whole session, not each break), when no trials are left, or at the day's turn.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Cultivator:
    up: bool = False
    day: date | None = None  # the scroll they went up on
    run_seen: bool = False  # a Cycles or Flow run was under way when last looked at


@dataclass(frozen=True)
class PeakFacts:
    """What is true of the scroll being worked, now."""

    day: date
    timer_running: bool  # any trial's timer, the one at hand or the one beside
    run_under_way: bool  # the room's Cycles run or Flow bank (paused counts)
    trials_left: bool  # a trial still waits on the scroll


def settle_cultivator(was: Cultivator, facts: PeakFacts) -> Cultivator:
    """Where the cultivator is now, given where they were when last looked at."""
    if facts.timer_running or facts.run_under_way:
        up = True
    elif was.day != facts.day or not facts.trials_left:
        up = False  # a new day, or nothing left to focus on
    elif was.run_seen:
        up = False  # the run ended since we last looked
    else:
        up = was.up  # a pause, a conquest, a step out: they meditate on
    return Cultivator(up=up, day=facts.day, run_seen=facts.run_under_way)
