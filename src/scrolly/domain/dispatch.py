"""The Scroll of Heavenly Tribulations and Ascendent Trials: today as Discord markdown. Pure.

The format is the owner's (`docs/prototype-notes.md`); `io/import_discord_md.py` reads it back.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from scrolly.domain.duration import format_duration
from scrolly.domain.legend import Legend, Symbol, type_of
from scrolly.domain.models import OPEN_STATES, Trial, TrialState

TITLE = "# :scroll: Scroll of Heavenly Tribulations and Ascendent Trials"
DND_LINE = "----- NO CHECK IN DND :crescent_moon:  -----"
REST_LINE = ":zzz:"  # plain sleep text, whatever shortcode stands for Postponed
END = "ENDE"


@dataclass(frozen=True)
class DispatchOptions:
    dnd: bool = False
    include_postponed: bool = False
    include_abandoned: bool = False


def _time(minutes: int | None) -> str:
    return "" if minutes is None else format_duration(minutes)


def _line(state: Symbol, legend: Legend, trial: Trial) -> str:
    kind = legend.types[type_of(trial.is_mandate, trial.art_kind)]
    estimate = (
        "" if trial.essence_expected_min is None else f" ({_time(trial.essence_expected_min)})"
    )
    return f"{state.shortcode} {kind.shortcode} {trial.title}{estimate}"


def _done_line(legend: Legend, trial: Trial) -> str:
    # A conquered trial always shows its parentheses and its actual time, so it reads back.
    kind = legend.types[type_of(trial.is_mandate, trial.art_kind)]
    state = legend.states[TrialState.DONE]
    head = f"{state.shortcode} {kind.shortcode} {trial.title}"
    return f"{head} ({_time(trial.essence_expected_min)}) >> {_time(trial.essence_actual_min or 0)}"


def render_dispatch(
    day: date, trials: Sequence[Trial], legend: Legend, options: DispatchOptions
) -> str:
    """Today's conquered, immediate and remaining trials, with the essence summary."""
    done = sorted(
        (t for t in trials if t.state is TrialState.DONE),
        key=lambda t: t.completed_at.timestamp() if t.completed_at else 0.0,
    )
    immediate = [t for t in trials if t.state is TrialState.IMMEDIATE]
    remaining = sorted(
        (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
    )
    counted = [t for t in trials if t.state is TrialState.DONE or t.state in OPEN_STATES]
    expected = sum(t.essence_expected_min or 0 for t in counted)
    actual = sum(t.essence_actual_min or 0 for t in done)

    lines = [TITLE, "", f"{day.day:02d}/{day.month:02d}/{day.year}"]
    if options.dnd:
        lines.append(DND_LINE)
    lines += [
        f"EXPECTED: {_time(expected)}",
        f"PROGRESS: {_time(actual)} / {_time(expected)}",
        "## Done",
        *(_done_line(legend, t) for t in done),
        "## Next",
        *(_line(legend.states[TrialState.IMMEDIATE], legend, t) for t in immediate),
        "## Remaining",
        *(_line(legend.states[TrialState.REMAINING], legend, t) for t in remaining),
    ]
    rest = legend.states[TrialState.REMAINING].shortcode
    lines += [f"{rest} {REST_LINE}", f"{rest} {END}"]
    if options.include_postponed:
        postponed = [t.title for t in trials if t.state is TrialState.POSTPONED]
        lines.append(f"Postponed: {', '.join(postponed)}".rstrip())
    if options.include_abandoned:
        abandoned = [t.title for t in trials if t.state is TrialState.LOST]
        lines.append(f"Abandoned: {', '.join(abandoned)}".rstrip())
    if options.dnd:
        lines += ["", DND_LINE]
    return "\n".join(lines) + "\n"
