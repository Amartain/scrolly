from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class TrialState(StrEnum):
    IMMEDIATE = "immediate"
    REMAINING = "remaining"
    DONE = "done"
    POSTPONED = "postponed"
    LOST = "lost"
    RETURNED = "returned"


OPEN_STATES = frozenset({TrialState.IMMEDIATE, TrialState.REMAINING})


class OriginType(StrEnum):
    BRAIN_DUMP = "brain_dump"
    HORIZON = "horizon"
    FOUNDATIONAL_ART = "foundational_art"
    RESTORATIVE_ART = "restorative_art"
    QUICK_ADD = "quick_add"


class ArtKind(StrEnum):
    FOUNDATIONAL = "foundational"
    RESTORATIVE = "restorative"


@dataclass(frozen=True)
class Trial:
    id: str
    logical_day: date
    title: str
    state: TrialState
    is_mandate: bool = False
    origin_type: OriginType = OriginType.BRAIN_DUMP
    origin_id: str | None = None
    position: int = 0
    essence_expected_min: int | None = None
    essence_actual_min: int | None = None
    completed_at: datetime | None = None
    note: str = ""
    timer_started_at: datetime | None = None
    timer_paused_at: datetime | None = None
    timer_accumulated_s: int = 0
    qi_expected: int | None = None
    # Set when the trial is conquered; blank means it cost what was estimated.
    qi_actual: int | None = None
    # An instance of an Art (its title matches one). Apart from `origin_type`: where it came from.
    art_kind: ArtKind | None = None


@dataclass(frozen=True)
class HorizonItem:
    id: str
    title: str
    is_mandate: bool = False
    essence_expected_min: int | None = None
    note: str = ""
    origin_type: OriginType = OriginType.BRAIN_DUMP
    origin_id: str | None = None
    qi_expected: int | None = None
    art_kind: ArtKind | None = None
    # Seconds already worked on it, so timing can go on after it is summoned again.
    worked_s: int = 0


@dataclass(frozen=True)
class Art:
    id: str
    kind: ArtKind
    title: str
    essence_expected_min: int | None = None
    note: str = ""
    qi_expected: int | None = None


@dataclass(frozen=True)
class Day:
    logical_day: date
    first_sealed_at: datetime | None = None
    rolled_over_at: datetime | None = None
    dusk_override: str | None = None
    advisor_silenced: bool = False
    qi_start: int | None = None
    poem_shown_at: datetime | None = None


class PlanPhase(StrEnum):
    INSCRIBE = "inscribe"
    ESTIMATE = "estimate"
    WEIGH = "weigh"


class PlanStatus(StrEnum):
    ZERO = "zero"
    INSCRIBE = "inscribe"
    ESTIMATE = "estimate"
    WEIGH = "weigh"
    ACTIVE = "active"


@dataclass(frozen=True)
class PlanningDraft:
    """Planning in progress for one logical day: phase, Phase 1 text and the chosen Qi start."""

    logical_day: date
    phase: PlanPhase = PlanPhase.INSCRIBE
    text: str = ""
    qi_start: int | None = None
