"""The day as tiles: one per trial, sized by what it took or is expected to take. Pure, no IO.

The dashboard draws the plan as a pale wash and what is done as solid ink, so both are always in
view. A conquered trial weighs what it really took; an open one, its estimate. The scale is the sum,
so a day that runs long simply grows and no tile is ever "over" (design principle 5).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from scrolly.domain.duration import format_duration
from scrolly.domain.models import ArtKind, Trial, TrialState
from scrolly.domain.qi import LINEAR_SPAN, effective_qi

# A trial with nothing to weigh (no estimate yet) still shows, as a narrow sliver of this many %.
SLIVER_PCT = 2.0


class TileState(StrEnum):
    DONE = "done"
    NOW = "now"
    WAITING = "waiting"


@dataclass(frozen=True)
class Tile:
    title: str
    state: TileState
    share_pct: float
    # The numbers of the tip, formatted; the interface words them. Taken: only once conquered.
    taken: str | None
    planned: str | None


@dataclass(frozen=True)
class QiRow:
    """Qi tiles on a scale of at least the day's start, so the room left before it shows."""

    tiles: list[Tile]
    harmonious_pct: float  # where Harmonious ends on the scale (the day's start)
    igniting_pct: float  # where Igniting the Blood ends


def day_order(trials: Sequence[Trial]) -> list[Trial]:
    """Conquered by when, then the trial at hand, then the waiting ones in the user's order."""
    done = sorted(
        (t for t in trials if t.state is TrialState.DONE),
        key=lambda t: t.completed_at.timestamp() if t.completed_at else 0.0,
    )
    now = [t for t in trials if t.state is TrialState.IMMEDIATE]
    waiting = sorted(
        (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
    )
    return [*done, *now, *waiting]


def _state(trial: Trial) -> TileState:
    if trial.state is TrialState.DONE:
        return TileState.DONE
    return TileState.NOW if trial.state is TrialState.IMMEDIATE else TileState.WAITING


def _shares(weights: Sequence[int], scale: float) -> list[float]:
    """Each weight as a share of the scale; weightless ones get a sliver, taken from the rest."""
    slivers = sum(1 for w in weights if w <= 0)
    room = max(0.0, 100.0 - slivers * SLIVER_PCT)
    return [SLIVER_PCT if w <= 0 else room * w / scale if scale > 0 else 0.0 for w in weights]


def essence_tiles(trials: Sequence[Trial]) -> list[Tile]:
    ordered = day_order(trials)
    weights = [
        (t.essence_actual_min or 0) if t.state is TrialState.DONE else (t.essence_expected_min or 0)
        for t in ordered
    ]
    shares = _shares(weights, sum(weights))
    return [
        Tile(
            t.title,
            _state(t),
            share,
            taken=_minutes(t.essence_actual_min or 0) if t.state is TrialState.DONE else None,
            planned=_minutes(t.essence_expected_min),
        )
        for t, share in zip(ordered, shares, strict=True)
    ]


def _minutes(value: int | None) -> str | None:
    return None if value is None else format_duration(value)


def qi_row(trials: Sequence[Trial], start: int) -> QiRow:
    """Qi tiles (Restorative Arts give Qi back, so they weigh nothing here) and the zone edges."""
    ordered = day_order(trials)
    weights = [0 if t.art_kind is ArtKind.RESTORATIVE else effective_qi(t) for t in ordered]
    scale = float(max(sum(weights), start + LINEAR_SPAN))
    shares = _shares(weights, scale)
    tiles = [
        Tile(
            t.title,
            _state(t),
            share,
            taken=str(effective_qi(t)) if t.state is TrialState.DONE else None,
            planned=None if t.qi_expected is None else str(t.qi_expected),
        )
        for t, share in zip(ordered, shares, strict=True)
    ]
    return QiRow(
        tiles=tiles,
        harmonious_pct=100 * start / scale,
        igniting_pct=min(100.0, 100 * (start + LINEAR_SPAN) / scale),
    )
