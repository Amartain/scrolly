"""What happens to trials once the day is sealed: conquer, postpone, abandon, revive, resummon.
Pure."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime

from scrolly.domain.art_match import with_title
from scrolly.domain.duration import parse_duration
from scrolly.domain.horizon import origin_key, return_to_horizon
from scrolly.domain.models import OPEN_STATES, Art, Day, HorizonItem, Trial, TrialState
from scrolly.domain.qi import check_qi, parse_qi
from scrolly.domain.timer import actual_minutes, pause, timer_ran


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


def require_editable(trial: Trial) -> None:
    """A conquered trial is read-only. To change it, revive it first."""
    if trial.state is TrialState.DONE:
        raise TrialError("A conquered trial is read-only. Revive it to change it.")


def promote_next(trials: Sequence[Trial], parallel_id: str | None = None) -> list[Trial]:
    """With no Immediate Trial, the unfinished parallel one (else the top Remaining) becomes it."""
    if immediate_of(trials) is not None:
        return []
    waiting = sorted(
        (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
    )
    beside = [t for t in waiting if t.id == parallel_id]
    chosen = (beside or waiting)[:1]
    return [replace(t, state=TrialState.IMMEDIATE) for t in chosen]


def conquer(trial: Trial, now: datetime, beside: bool = False) -> Trial:
    """Finish the Immediate Trial (`beside`: the parallel one): stop its timer, record minutes."""
    if beside:
        _require(trial, TrialState.REMAINING, "Only the parallel trial can be conquered here")
    else:
        _require(trial, TrialState.IMMEDIATE, "Only the Immediate Trial can be conquered")
    return replace(
        pause(trial, now),
        state=TrialState.DONE,
        essence_actual_min=actual_minutes(trial, now),
        qi_actual=trial.qi_expected,
        completed_at=now,
    )


def set_actual_qi(trial: Trial, qi: int) -> Trial:
    """The Qi a conquered trial really took. Conquering records the estimate; this corrects it."""
    _require(trial, TrialState.DONE, "Only a conquered trial's Qi can be set")
    return replace(trial, qi_actual=check_qi(qi))


def set_actual_minutes(trial: Trial, text: str) -> Trial:
    """The time a conquered trial really took, as the user corrects it ("45m", "+1h5m").

    The timer holds the same total, so a later Revive carries on from the corrected time.
    """
    _require(trial, TrialState.DONE, "Only a conquered trial's time can be corrected")
    minutes = parse_duration(text.strip().removeprefix("+"))
    if minutes is None:
        raise TrialError("Write the time it took, for example 45m")
    return replace(trial, essence_actual_min=minutes, timer_accumulated_s=minutes * 60)


def postpone(
    trial: Trial, horizon: Sequence[HorizonItem], now: datetime
) -> tuple[Trial, list[HorizonItem]]:
    """Send an open trial to the top of the Horizon (estimate and the time worked are kept)."""
    _require_open(trial, "Only an open trial can be postponed")
    stopped = pause(trial, now)
    return replace(stopped, state=TrialState.POSTPONED), return_to_horizon(horizon, stopped)


def abandon(trial: Trial, now: datetime) -> Trial:
    """Let a Mortal Trial go. A Heavenly Mandate is never abandoned: it is postponed.

    The minutes it was timed still count as Essence expended (none if it never ran).
    """
    _require_open(trial, "Only an open trial can be abandoned")
    if trial.is_mandate:
        raise TrialError("A Heavenly Mandate cannot be abandoned. Postpone it to the Horizon.")
    spent = actual_minutes(trial, now) if timer_ran(trial) else None
    return replace(pause(trial, now), state=TrialState.LOST, essence_actual_min=spent)


def revive(trial: Trial, trials: Sequence[Trial]) -> Trial:
    """Undo a conquest: Immediate if nothing is underway, else the top of the Remaining queue.

    The time already on the timer stays, so nothing is lost.
    """
    _require(trial, TrialState.DONE, "Only a conquered trial can be revived")
    cleared = replace(trial, essence_actual_min=None, qi_actual=None, completed_at=None)
    return _back_on_scroll(cleared, trials)


def resummon(
    trial: Trial, trials: Sequence[Trial], horizon: Sequence[HorizonItem]
) -> tuple[Trial, list[HorizonItem]]:
    """Bring back a trial postponed or let go today (owner, 2026-10-23: a double-click), as Revive
    does: Immediate if nothing is underway, else the top of Remaining. Its time stays; a postponed
    trial leaves the Horizon again."""
    if trial.state not in (TrialState.POSTPONED, TrialState.LOST):
        raise TrialError("Only a postponed or abandoned trial can be summoned back")
    key = origin_key(trial)
    kept = [item for item in horizon if key not in (item.id, item.origin_id)]
    back = _back_on_scroll(replace(trial, essence_actual_min=None), trials)
    return back, kept if trial.state is TrialState.POSTPONED else list(horizon)


def _back_on_scroll(trial: Trial, trials: Sequence[Trial]) -> Trial:
    """Immediate if nothing is underway, else the top of the Remaining queue."""
    if immediate_of(trials) is None:
        return replace(trial, state=TrialState.IMMEDIATE)
    top = min(t.position for t in trials if t.state in OPEN_STATES)
    return replace(trial, state=TrialState.REMAINING, position=top - 1)


def set_estimate(trial: Trial, text: str) -> Trial:
    """The time expected of an open trial. It is set once: a trial that has one keeps it."""
    _require_open(trial, "Only an open trial's estimate can be changed")
    if trial.essence_expected_min is not None:
        raise TrialError("The estimate is already set")
    return replace(trial, essence_expected_min=parse_duration(text))


def set_estimated_qi(trial: Trial, text: str) -> Trial:
    """The Qi expected of an open trial. It is set once: a trial that has one keeps it."""
    _require_open(trial, "Only an open trial's estimate can be changed")
    if trial.qi_expected is not None:
        raise TrialError("The Qi estimate is already set")
    return replace(trial, qi_expected=parse_qi(text))


def rename(trial: Trial, title: str, arts: Sequence[Art] = ()) -> Trial:
    """A new title. Naming an Art makes the trial an instance of it; leaving the name ends that."""
    cleaned = title.strip()
    if not cleaned:
        raise TrialError("A trial needs a title")
    return with_title(trial, cleaned, arts)


def is_victory(day: Day | None, trials: Sequence[Trial]) -> bool:
    """The sun sets on the peak: the day began, something was conquered and nothing is left open."""
    if day is None or day.first_sealed_at is None:
        return False
    if any(t.state in OPEN_STATES for t in trials):
        return False
    return any(t.state is TrialState.DONE for t in trials)
