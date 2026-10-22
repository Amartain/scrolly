"""The day's time summary: minutes done against minutes expected. Pure, no IO."""

from collections.abc import Sequence
from dataclasses import dataclass

from scrolly.domain.models import OPEN_STATES, Trial, TrialState

SPENT_STATES = frozenset({TrialState.DONE, TrialState.LOST})


@dataclass(frozen=True)
class EssenceSummary:
    actual_min: int
    expected_min: int
    remaining_min: int
    meter_pct: int

    @property
    def blank(self) -> bool:
        """Nothing estimated and nothing spent yet: there is nothing for the meter to show."""
        return self.expected_min == 0 and self.actual_min == 0


def essence_summary(trials: Sequence[Trial]) -> EssenceSummary:
    """Minutes spent (conquered, or timed before being let go) against the estimates of everything
    conquered or still open.

    Postponed and let-go trials leave the plan, so their estimates count toward neither side.
    """
    done = [t for t in trials if t.state is TrialState.DONE]
    open_ = [t for t in trials if t.state in OPEN_STATES]
    actual = sum(t.essence_actual_min or 0 for t in trials if t.state in SPENT_STATES)
    remaining = sum(t.essence_expected_min or 0 for t in open_)
    expected = sum(t.essence_expected_min or 0 for t in done) + remaining
    meter = 0 if expected <= 0 else min(100, round(100 * actual / expected))
    return EssenceSummary(actual, expected, remaining, meter)
