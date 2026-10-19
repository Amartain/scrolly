"""Titles stay unique where it matters. Trials are one-time events; Arts are practices. Pure.

A trial title may be on the Horizon or on today's scroll, never both and never twice. Earlier days,
Fallen Leaves and abandoned trials do not count. Art copies on the scroll are skipped, because
summoning an Art again and again is allowed. Titles match trimmed and case-insensitive.
"""

from collections.abc import Sequence
from enum import StrEnum

from scrolly.domain.horizon import same_title
from scrolly.domain.models import Art, ArtKind, HorizonItem, Trial, TrialState
from scrolly.domain.planning import is_art_copy

_ON_THE_SCROLL = frozenset({TrialState.IMMEDIATE, TrialState.REMAINING, TrialState.DONE})


class DuplicateTitleError(ValueError):
    """A title that is already taken. The message is shown to the user."""


class Place(StrEnum):
    HORIZON = "the Horizon"
    TODAY = "today's scroll"


def trial_title_taken(
    title: str,
    horizon: Sequence[HorizonItem],
    today_trials: Sequence[Trial],
    *,
    except_id: str | None = None,
) -> Place | None:
    """Where this title already lives, or None. `except_id` is the item being renamed."""
    if any(same_title(i.title, title) for i in horizon if i.id != except_id):
        return Place.HORIZON
    if any(
        same_title(t.title, title)
        for t in today_trials
        if t.id != except_id and t.state in _ON_THE_SCROLL and not is_art_copy(t)
    ):
        return Place.TODAY
    return None


def art_title_taken(
    title: str, arts: Sequence[Art], kind: ArtKind, *, except_id: str | None = None
) -> bool:
    return any(a.kind is kind and a.id != except_id and same_title(a.title, title) for a in arts)


def require_free_trial_title(
    title: str,
    horizon: Sequence[HorizonItem],
    today_trials: Sequence[Trial],
    *,
    except_id: str | None = None,
) -> None:
    place = trial_title_taken(title, horizon, today_trials, except_id=except_id)
    if place is not None:
        raise DuplicateTitleError(f"Already on {place.value}: {title.strip()}")


def require_free_art_title(
    title: str, arts: Sequence[Art], kind: ArtKind, *, except_id: str | None = None
) -> None:
    if art_title_taken(title, arts, kind, except_id=except_id):
        raise DuplicateTitleError(f"That Art is already in this list: {title.strip()}")


def require_free_dump(
    lines: Sequence[str], horizon: Sequence[HorizonItem], today_trials: Sequence[Trial]
) -> None:
    """Phase 1: no line may repeat or already exist. The note names every offender."""
    seen: set[str] = set()
    repeated: list[str] = []
    for line in lines:
        key = line.strip().casefold()
        if key in seen and line not in repeated:
            repeated.append(line)
        seen.add(key)
    notes = [f"Written twice: {', '.join(repeated)}"] if repeated else []
    for place in Place:
        taken = [x for x in lines if trial_title_taken(x, horizon, today_trials) is place]
        if taken:
            notes.append(f"Already on {place.value}: {', '.join(taken)}")
    if notes:
        raise DuplicateTitleError(". ".join(notes))
