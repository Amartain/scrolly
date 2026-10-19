"""Titles stay unique where it matters. Trials are one-time events; Arts are practices. Pure.

A trial title may be on the Horizon or on today's scroll, never both and never twice. Earlier days,
Fallen Leaves and abandoned trials do not count. A title that names an Art makes an instance of
that Art. Instances repeat freely, so such a title is never refused and instances never block one.
Titles match trimmed and case-insensitive.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from scrolly.domain.art_match import art_kind_for
from scrolly.domain.horizon import same_title
from scrolly.domain.models import Art, ArtKind, HorizonItem, Trial, TrialState

_ON_THE_SCROLL = frozenset({TrialState.IMMEDIATE, TrialState.REMAINING, TrialState.DONE})


@dataclass(frozen=True)
class Refusal:
    """Which titles were refused and why. The interface words it; Python only reports the facts."""

    repeated: list[str] = field(default_factory=list)
    horizon: list[str] = field(default_factory=list)
    today: list[str] = field(default_factory=list)
    art: list[str] = field(default_factory=list)


class DuplicateTitleError(ValueError):
    """A title that is already taken. `str(error)` is a plain fallback; `refusal` has the facts."""

    def __init__(self, message: str, refusal: Refusal) -> None:
        super().__init__(message)
        self.refusal = refusal


class Place(StrEnum):
    HORIZON = "the Horizon"
    TODAY = "today's scroll"


def trial_title_taken(
    title: str,
    horizon: Sequence[HorizonItem],
    today_trials: Sequence[Trial],
    arts: Sequence[Art] = (),
    *,
    except_id: str | None = None,
) -> Place | None:
    """Where this title already lives, or None. `except_id` is the item being renamed."""
    if art_kind_for(title, arts) is not None:
        return None
    if any(same_title(i.title, title) for i in horizon if i.id != except_id and i.art_kind is None):
        return Place.HORIZON
    if any(
        same_title(t.title, title)
        for t in today_trials
        if t.id != except_id and t.state in _ON_THE_SCROLL and t.art_kind is None
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
    arts: Sequence[Art] = (),
    *,
    except_id: str | None = None,
) -> None:
    place = trial_title_taken(title, horizon, today_trials, arts, except_id=except_id)
    if place is not None:
        cleaned = title.strip()
        where = Refusal(horizon=[cleaned]) if place is Place.HORIZON else Refusal(today=[cleaned])
        raise DuplicateTitleError(f"Already on {place.value}: {cleaned}", where)


def require_free_art_title(
    title: str, arts: Sequence[Art], kind: ArtKind, *, except_id: str | None = None
) -> None:
    if art_title_taken(title, arts, kind, except_id=except_id):
        cleaned = title.strip()
        raise DuplicateTitleError(
            f"That Art is already in this list: {cleaned}", Refusal(art=[cleaned])
        )


def require_free_dump(
    lines: Sequence[str],
    horizon: Sequence[HorizonItem],
    today_trials: Sequence[Trial],
    arts: Sequence[Art] = (),
) -> None:
    """Phase 1: no plain line may repeat or exist already; Art lines are exempt. Names offenders."""
    plain = [x for x in lines if art_kind_for(x, arts) is None]
    seen: set[str] = set()
    repeated: list[str] = []
    for line in plain:
        key = line.strip().casefold()
        if key in seen and line not in repeated:
            repeated.append(line)
        seen.add(key)
    notes = [f"Written twice: {', '.join(repeated)}"] if repeated else []
    found: dict[Place, list[str]] = {}
    for place in Place:
        found[place] = [x for x in plain if trial_title_taken(x, horizon, today_trials) is place]
        if found[place]:
            notes.append(f"Already on {place.value}: {', '.join(found[place])}")
    if notes:
        refusal = Refusal(repeated=repeated, horizon=found[Place.HORIZON], today=found[Place.TODAY])
        raise DuplicateTitleError(". ".join(notes), refusal)
