"""Parallel Flow: a trial of its own run beside the one at hand. Pure, no IO.

A parallel trial is never part of the main trial: its time, qi and conquest are its own. Only one
runs at a time. It is found among the waiting trials, the Arts and the Horizon, or made on the spot.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.models import Art, HorizonItem, Trial, TrialState

MAX_CANDIDATES = 8


class Source(StrEnum):
    REMAINING = "remaining"
    ART = "art"
    HORIZON = "horizon"


@dataclass(frozen=True)
class Candidate:
    source: Source
    id: str
    title: str
    type: TrialType


def find_candidates(
    query: str,
    trials: Sequence[Trial],
    arts: Sequence[Art],
    horizon: Sequence[HorizonItem],
    main_id: str | None,
) -> list[Candidate]:
    """What the search bar offers: waiting trials first, then Arts, then the Horizon.

    The trial at hand is never offered; a trial cannot be both main and parallel.
    """
    needle = query.strip().casefold()
    if not needle:
        return []
    found = [
        Candidate(Source.REMAINING, t.id, t.title, type_of(t.is_mandate, t.art_kind))
        for t in sorted(trials, key=lambda t: t.position)
        if t.state is TrialState.REMAINING and t.id != main_id and needle in t.title.casefold()
    ]
    found += [
        Candidate(Source.ART, a.id, a.title, type_of(False, a.kind))
        for a in arts
        if needle in a.title.casefold()
    ]
    found += [
        Candidate(Source.HORIZON, h.id, h.title, type_of(h.is_mandate, h.art_kind))
        for h in horizon
        if needle in h.title.casefold()
    ]
    return found[:MAX_CANDIDATES]


def can_run_beside(trial: Trial, main_id: str | None, parallel_id: str | None) -> bool:
    """A waiting trial may run beside the main one, if none already does."""
    return trial.state is TrialState.REMAINING and trial.id != main_id and parallel_id is None
