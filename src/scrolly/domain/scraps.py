"""Bamboo Scraps: loose thoughts jotted during one visit to Seclusion. Pure, no IO.

A scrap spans from opening Seclusion to leaving it, and notes the trials worked on in the order
they were first started. It is saved as it is written, so a crash closes it at the last save. An
empty scrap is not kept.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime

from scrolly.domain.segments import Segment


@dataclass(frozen=True)
class Scrap:
    id: str
    opened_at: datetime
    saved_at: datetime
    closed_at: datetime | None = None
    text: str = ""
    trial_ids: tuple[str, ...] = ()

    @property
    def is_open(self) -> bool:
        return self.closed_at is None


def open_scrap(scrap_id: str, now: datetime) -> Scrap:
    return Scrap(scrap_id, opened_at=now, saved_at=now)


def write_scrap(scrap: Scrap, text: str, now: datetime) -> Scrap:
    return replace(scrap, text=text, saved_at=now)


def note_trial(scrap: Scrap, trial_id: str) -> Scrap:
    """A trial worked on during the visit, noted the first time only."""
    if trial_id in scrap.trial_ids:
        return scrap
    return replace(scrap, trial_ids=(*scrap.trial_ids, trial_id))


def close_scrap(scrap: Scrap, now: datetime) -> Scrap:
    """The visit ended. A scrap that has closed stays as it was."""
    return scrap if scrap.closed_at is not None else replace(scrap, closed_at=now)


def close_after_crash(scrap: Scrap) -> Scrap:
    """A scrap found still open from an earlier visit ended where it was last saved."""
    return close_scrap(scrap, scrap.saved_at)


def is_kept(scrap: Scrap) -> bool:
    """Only a scrap with something written on it is kept."""
    return bool(scrap.text.strip())


@dataclass(frozen=True)
class Lane:
    """When one trial was worked during a visit: stretches as seconds from the visit's start."""

    trial_id: str
    spans: tuple[tuple[int, int], ...]


def visit_seconds(scrap: Scrap) -> int:
    """How long the visit lasted. A scrap still open has no length yet."""
    if scrap.closed_at is None:
        return 0
    return max(0, int((scrap.closed_at - scrap.opened_at).total_seconds()))


def scrap_lanes(scrap: Scrap, segments: Mapping[str, Sequence[Segment]]) -> list[Lane]:
    """One lane per trial worked, in the order they were started. Stretches may overlap.

    Each trial's timer segments are cut to the visit, so two trials run side by side show as two
    lanes lit at the same time.
    """
    if scrap.closed_at is None:
        return []
    lanes = []
    for trial_id in scrap.trial_ids:
        spans = []
        for segment in segments.get(trial_id, ()):
            start = max(segment.started_at, scrap.opened_at)
            end = min(segment.ended_at or scrap.closed_at, scrap.closed_at)
            if end > start:
                first = int((start - scrap.opened_at).total_seconds())
                spans.append((first, int((end - scrap.opened_at).total_seconds())))
        lanes.append(Lane(trial_id, tuple(sorted(spans))))
    return lanes
