"""The two lifetime counters on the dashboard. Pure, and they only ever go up."""

from collections.abc import Sequence

from scrolly.domain.models import Day, Trial, TrialState


def lifetime_conquered(trials: Sequence[Trial]) -> int:
    """Every trial ever conquered, on any day. Reviving one takes it back out."""
    return sum(1 for t in trials if t.state is TrialState.DONE)


def heavenly_cycles(days: Sequence[Day]) -> int:
    """Days the scroll was sealed. A day counts once, however often it was sealed."""
    return sum(1 for d in days if d.first_sealed_at is not None)
