"""The queue of a sealed day: scribe a trial, promote a waiting one, reorder them. Pure."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import date, datetime

from scrolly.domain.advisor import postponable_mandates
from scrolly.domain.art_match import art_kind_for
from scrolly.domain.day_flow import TrialError, immediate_of, postpone
from scrolly.domain.duration import parse_duration
from scrolly.domain.models import Art, HorizonItem, Trial, TrialState
from scrolly.domain.planning import next_position, trial_from_line
from scrolly.domain.qi import parse_qi
from scrolly.domain.timer import pause


def scribe(
    trial_id: str,
    title: str,
    estimate: str,
    qi: str,
    day: date,
    trials: Sequence[Trial],
    arts: Sequence[Art] = (),
) -> Trial:
    """A new trial for a sealed day: Immediate if nothing is underway, else on top of Remaining.

    A sudden trial is the next thing to do, so it goes ahead of the ones already waiting.
    A title that names an Art makes an instance of it.
    """
    cleaned = title.strip()
    if not cleaned:
        raise TrialError("A trial needs a title")
    kind = art_kind_for(cleaned, arts)
    line = trial_from_line(trial_id, cleaned, day, next_position(trials), kind)
    state = TrialState.REMAINING if immediate_of(trials) else TrialState.IMMEDIATE
    waiting = [t.position for t in trials if t.state is TrialState.REMAINING]
    return replace(
        line,
        state=state,
        position=min(waiting) - 1 if waiting else line.position,
        essence_expected_min=parse_duration(estimate),
        qi_expected=parse_qi(qi),
    )


def promote(trial: Trial, trials: Sequence[Trial], now: datetime) -> list[Trial]:
    """Make a waiting trial Immediate. The one underway steps back to the top of the queue."""
    if trial.state is not TrialState.REMAINING:
        raise TrialError("Only a Remaining Trial can be promoted")
    changed = [replace(trial, state=TrialState.IMMEDIATE)]
    current = immediate_of(trials)
    if current is not None:
        top = min(t.position for t in trials if t.state is TrialState.REMAINING)
        stepped_back = replace(pause(current, now), state=TrialState.REMAINING, position=top - 1)
        changed.append(stepped_back)
    return changed


def postpone_mandates(
    trials: Sequence[Trial], horizon: Sequence[HorizonItem], now: datetime
) -> tuple[list[Trial], list[HorizonItem]]:
    """Send the waiting Mandates to the top of the Horizon, with the time worked and in their order.

    The Immediate Trial stays: it is the one being done.
    """
    items = list(horizon)
    changed: list[Trial] = []
    # Last first, so the one that was on top ends on top.
    for trial in reversed(postponable_mandates(trials)):
        gone, items = postpone(trial, items, now)
        changed.append(gone)
    return changed, items


def reorder_remaining(trials: Sequence[Trial], ids: Sequence[str]) -> list[Trial]:
    """The waiting trials in a new order, on the same positions. `ids` names each once."""
    waiting = [t for t in trials if t.state is TrialState.REMAINING]
    if len(set(ids)) != len(ids) or set(ids) != {t.id for t in waiting}:
        raise TrialError("The new order must list every Remaining Trial once")
    by_id = {t.id: t for t in waiting}
    slots = sorted(t.position for t in waiting)
    return [
        replace(by_id[trial_id], position=slot) for trial_id, slot in zip(ids, slots, strict=True)
    ]
