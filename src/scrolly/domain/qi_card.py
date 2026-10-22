"""The card after a conquest: three likely answers, and the day's Qi for one. Pure, no IO."""

from collections.abc import Sequence
from dataclasses import dataclass, replace

from scrolly.domain import qi
from scrolly.domain.models import Trial

HEAVIER_STEP = 5  # the least "Heavier" adds, so an estimate of 0 or 2 still has a heavier answer


@dataclass(frozen=True)
class QiChoices:
    lighter: int
    foreseen: int
    heavier: int


def qi_choices(estimate: int) -> QiChoices:
    """Half the estimate, the estimate, and half again (at least a few more), within 0-100."""
    heavier = max(estimate + estimate // 2, estimate + HEAVIER_STEP)
    return QiChoices(estimate // 2, estimate, min(qi.QI_PER_TRIAL_MAX, heavier))


def spent_if(trials: Sequence[Trial], trial_id: str, value: int) -> int:
    """The day's spent Qi if this conquered trial took `value`."""
    return qi.spent([replace(t, qi_actual=value) if t.id == trial_id else t for t in trials])
