"""What happens to trials once the day is sealed: conquer, postpone, abandon, revive. Pure."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from scrolly.domain.duration import parse_duration
from scrolly.domain.horizon import return_to_horizon
from scrolly.domain.models import OPEN_STATES, Day, HorizonItem, Trial, TrialState
from scrolly.domain.qi import parse_qi
from scrolly.domain.timer import actual_minutes, pause


class TrialError(ValueError):
    """A step that cannot happen to this trial right now. The message is shown to the user."""


def _require(trial: Trial, state: TrialState, refusal: str) -> None:
    if trial.state is not state:
        raise TrialError(refusal)


def _require_open(trial: Trial, refusal: str) -> None:
    if trial.state not in OPEN_STATES:
        raise TrialError(refusal)


def immediate_of(trials: Sequence[Trial]) -> Trial | None:
    return next((t for t in trials if t.state is TrialState.IMMEDIATE), None)


def promote_next(trials: Sequence[Trial]) -> list[Trial]:
    """With no Immediate Trial, the first Remaining one becomes it. Returns what changed."""
    if immediate_of(trials) is not None:
        return []
    waiting = sorted(
        (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
    )
    return [replace(waiting[0], state=TrialState.IMMEDIATE)] if waiting else []


def conquer(trial: Trial, now: datetime) -> Trial:
    """Finish the Immediate Trial: stop the timer, record the timed minutes (else the estimate)."""
    _require(trial, TrialState.IMMEDIATE, "Only the Immediate Trial can be conquered")
    return replace(
        pause(trial, now),
        state=TrialState.DONE,
        essence_actual_min=actual_minutes(trial, now),
        qi_actual=trial.qi_expected,
        completed_at=now,
    )


def postpone(
    trial: Trial, horizon: Sequence[HorizonItem], now: datetime
) -> tuple[Trial, list[HorizonItem]]:
    """Send an open trial to the top of the Horizon (estimate kept, time not carried)."""
    _require_open(trial, "Only an open trial can be postponed")
    return replace(pause(trial, now), state=TrialState.POSTPONED), return_to_horizon(horizon, trial)


def abandon(trial: Trial, now: datetime) -> Trial:
    """Let a Mortal Trial go. A Heavenly Mandate is never abandoned: it is postponed."""
    _require_open(trial, "Only an open trial can be abandoned")
    if trial.is_mandate:
        raise TrialError("A Heavenly Mandate cannot be abandoned. Postpone it to the Horizon.")
    return replace(pause(trial, now), state=TrialState.LOST)


def revive(trial: Trial, trials: Sequence[Trial]) -> Trial:
    """Undo a conquest: Immediate if nothing is underway, else the top of the Remaining queue.

    The time already on the timer stays, so nothing is lost.
    """
    _require(trial, TrialState.DONE, "Only a conquered trial can be revived")
    cleared = replace(trial, essence_actual_min=None, qi_actual=None, completed_at=None)
    if immediate_of(trials) is None:
        return replace(cleared, state=TrialState.IMMEDIATE)
    top = min(t.position for t in trials if t.state in OPEN_STATES)
    return replace(cleared, state=TrialState.REMAINING, position=top - 1)


def set_actual(trial: Trial, text: str) -> Trial:
    """Correct the minutes recorded for a conquered trial. Blank clears them."""
    _require(trial, TrialState.DONE, "Only a conquered trial's minutes can be corrected")
    return replace(trial, essence_actual_min=parse_duration(text))


def set_estimate(trial: Trial, text: str) -> Trial:
    """The time expected of a trial that is still open. Blank clears it."""
    _require_open(trial, "Only an open trial's estimate can be changed")
    return replace(trial, essence_expected_min=parse_duration(text))


def set_actual_qi(trial: Trial, text: str) -> Trial:
    """Correct the Qi recorded for a conquered trial. Blank means it cost what was estimated."""
    _require(trial, TrialState.DONE, "Only a conquered trial's Qi can be corrected")
    return replace(trial, qi_actual=parse_qi(text))


def set_estimated_qi(trial: Trial, text: str) -> Trial:
    """The Qi expected of a trial that is still open. Blank clears it."""
    if trial.state not in OPEN_STATES:
        raise TrialError("Only an open trial's estimate can be changed")
    return replace(trial, qi_expected=parse_qi(text))


def rename(trial: Trial, title: str) -> Trial:
    cleaned = title.strip()
    if not cleaned:
        raise TrialError("A trial needs a title")
    return replace(trial, title=cleaned)


def is_victory(day: Day | None, trials: Sequence[Trial]) -> bool:
    """The sun sets on the peak: the day began, something was conquered and nothing is left open."""
    if day is None or day.first_sealed_at is None:
        return False
    if any(t.state in OPEN_STATES for t in trials):
        return False
    return any(t.state is TrialState.DONE for t in trials)
