"""Trial of the Incense: pacing focus against the estimate, with one gentle gong. Pure, no IO."""

from dataclasses import dataclass
from enum import StrEnum

GONG_EVERY_S = 30 * 60


class IncenseState(StrEnum):
    REMAINING = "remaining"
    OVERFILLED = "overfilled"


@dataclass(frozen=True)
class IncenseView:
    state: IncenseState
    remaining_s: int
    over_s: int


def ring_elapsed(elapsed_s: int, baseline_s: int = 0) -> int:
    """Time on the ring's current timer: the trial's logged time since New timer or Zero out.

    A baseline above the logged time is stale (the trial's own timer was reset), so it is ignored.
    """
    return elapsed_s - baseline_s if elapsed_s >= baseline_s else elapsed_s


def incense_view(ring_s: int, expected_s: int) -> IncenseView:
    """Counting down to the estimate, then counting up past it ("overfilled", never "overdue")."""
    if ring_s < expected_s:
        return IncenseView(IncenseState.REMAINING, expected_s - ring_s, 0)
    return IncenseView(IncenseState.OVERFILLED, 0, ring_s - expected_s)


def seconds_to_gong(ring_s: int, expected_s: int) -> int:
    """Seconds until the next gong: the estimate running out, then every 30 minutes after it."""
    over = ring_s - expected_s
    return -over if over < 0 else GONG_EVERY_S - over % GONG_EVERY_S
