"""The daily planning rules: what a scroll is made of and how it is sealed. Pure, no IO."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import date, datetime

from scrolly.domain.duration import parse_duration
from scrolly.domain.horizon import return_to_horizon
from scrolly.domain.models import (
    Art,
    ArtKind,
    Day,
    HorizonItem,
    OriginType,
    PlanningDraft,
    PlanStatus,
    Trial,
    TrialState,
)
from scrolly.domain.qi import parse_qi


class PlanningError(ValueError):
    """A planning step that cannot happen right now. The message is shown to the user."""


def planning_status(day: Day | None, draft: PlanningDraft | None) -> PlanStatus:
    if day is not None and day.first_sealed_at is not None:
        return PlanStatus.ACTIVE
    return PlanStatus(draft.phase.value) if draft is not None else PlanStatus.ZERO


def dump_lines(text: str) -> list[str]:
    """One trial per non-empty line."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def next_position(trials: Sequence[Trial]) -> int:
    return max((t.position for t in trials), default=-1) + 1


def trial_from_line(trial_id: str, title: str, day: date, position: int) -> Trial:
    return Trial(
        id=trial_id,
        logical_day=day,
        title=title,
        state=TrialState.REMAINING,
        origin_type=OriginType.BRAIN_DUMP,
        position=position,
    )


def trial_from_horizon(trial_id: str, item: HorizonItem, day: date, position: int) -> Trial:
    return Trial(
        id=trial_id,
        logical_day=day,
        title=item.title,
        state=TrialState.REMAINING,
        is_mandate=item.is_mandate,
        origin_type=OriginType.HORIZON,
        origin_id=item.id,
        position=position,
        essence_expected_min=item.essence_expected_min,
        note=item.note,
        qi_expected=item.qi_expected,
    )


def trial_from_art(trial_id: str, art: Art, day: date, position: int) -> Trial:
    origin = (
        OriginType.FOUNDATIONAL_ART
        if art.kind is ArtKind.FOUNDATIONAL
        else OriginType.RESTORATIVE_ART
    )
    return Trial(
        id=trial_id,
        logical_day=day,
        title=art.title,
        state=TrialState.REMAINING,
        origin_type=origin,
        origin_id=art.id,
        position=position,
        essence_expected_min=art.essence_expected_min,
        note=art.note,
        qi_expected=art.qi_expected,
    )


def is_art_copy(trial: Trial) -> bool:
    return trial.origin_type in (OriginType.FOUNDATIONAL_ART, OriginType.RESTORATIVE_ART)


def unstage(trial: Trial, horizon: Sequence[HorizonItem]) -> list[HorizonItem]:
    """Take a trial off the scroll. Only a Horizon item goes back; copies and lines just go."""
    if trial.origin_type is OriginType.HORIZON:
        return return_to_horizon(horizon, trial)
    return list(horizon)


def abandon(trials: Sequence[Trial], horizon: Sequence[HorizonItem]) -> list[HorizonItem]:
    """Give back everything the scroll took from the Horizon."""
    items = list(horizon)
    for trial in trials:
        items = unstage(trial, items)
    return items


def dismiss(trial: Trial, horizon: Sequence[HorizonItem]) -> tuple[Trial, list[HorizonItem]]:
    """A Mortal Trial is let go (lost). A Mandate is postponed to the top of the Horizon."""
    if trial.is_mandate:
        return replace(trial, state=TrialState.POSTPONED), return_to_horizon(horizon, trial)
    return replace(trial, state=TrialState.LOST), list(horizon)


def set_estimate(trial: Trial, text: str) -> Trial:
    return replace(trial, essence_expected_min=parse_duration(text))


def set_qi(trial: Trial, text: str) -> Trial:
    return replace(trial, qi_expected=parse_qi(text))


def set_mandate(trial: Trial, is_mandate: bool) -> Trial:
    if is_mandate and is_art_copy(trial):
        raise PlanningError("Arts cannot be Heavenly Mandates")
    return replace(trial, is_mandate=is_mandate)


def reorder(trials: Sequence[Trial], ids: Sequence[str]) -> list[Trial]:
    """New positions in the given order. The ids must be exactly the trials being ordered."""
    if len(set(ids)) != len(ids) or set(ids) != {t.id for t in trials}:
        raise PlanningError("The new order must list every trial on the scroll once")
    by_id = {t.id: t for t in trials}
    return [replace(by_id[trial_id], position=i) for i, trial_id in enumerate(ids)]


def seal(
    trials: Sequence[Trial], day: Day, now: datetime, qi_start: int | None = None
) -> tuple[Trial, Day]:
    """Start the day: the first trial becomes Immediate. Only the first seal of a day counts.

    `qi_start` is the Golden Core's chosen start (None when the Golden Core is off).
    """
    waiting = sorted(
        (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
    )
    if not waiting:
        raise PlanningError("Put at least one trial on the scroll before sealing it")
    first = replace(waiting[0], state=TrialState.IMMEDIATE)
    return first, replace(day, first_sealed_at=day.first_sealed_at or now, qi_start=qi_start)
