"""The Scroll of Heavenly Tribulations and Ascendent Trials: today as Discord markdown. Pure.

The format is the owner's (`docs/prototype-notes.md`); `io/import_discord_md.py` reads it back.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from scrolly.domain.beside import Beside
from scrolly.domain.duration import format_duration
from scrolly.domain.legend import Legend, Symbol, type_of
from scrolly.domain.models import OPEN_STATES, Trial, TrialState

TITLE = "# :scroll: Scroll of Heavenly Tribulations and Ascendent Trials"
DND_LINE = "----- NO CHECK IN DND :crescent_moon:  -----"
REST_LINE = ":zzz:"  # plain sleep text, whatever shortcode stands for Postponed
END = "ENDE"
BESIDE = "⇄"  # a Done line run in Parallel Flow ends with this and the trial it ran beside


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


def _done_line(legend: Legend, trial: Trial, partner: str | None) -> str:
    # A conquered trial always shows its parentheses and its actual time, so it reads back.
    kind = legend.types[type_of(trial.is_mandate, trial.art_kind)]
    state = legend.states[TrialState.DONE]
    head = f"{state.shortcode} {kind.shortcode} {trial.title}"
    line = f"{head} ({_time(trial.essence_expected_min)}) >> {_time(trial.essence_actual_min or 0)}"
    return line if partner is None else f"{line} {BESIDE} {partner}".rstrip()


def render_dispatch(
    day: date,
    trials: Sequence[Trial],
    legend: Legend,
    options: DispatchOptions,
    beside: Mapping[str, Beside] | None = None,
    focus_min: int | None = None,
) -> str:
    """Today's conquered, immediate and remaining trials, with the essence summary.

    Time run beside another trial (Parallel Flow) is marked on its line and noted in PROGRESS; then
    FOCUS says how long the day took on the clock, since the sum counts that time twice.
    """
    beside = beside or {}
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
    titles = {t.id: t.title for t in trials}
    side = {t.id: beside[t.id] for t in done if t.id in beside and beside[t.id].minutes > 0}
    side_min = sum(b.minutes for b in side.values())
    progress = f"PROGRESS: {_time(actual)} / {_time(expected)}"

    lines = [TITLE, "", f"{day.day:02d}/{day.month:02d}/{day.year}"]
    if options.dnd:
        lines.append(DND_LINE)
    lines += [
        f"EXPECTED: {_time(expected)}",
        f"{progress} ({_time(side_min)} beside)" if side_min else progress,
        *([f"FOCUS: {_time(focus_min)}"] if side_min and focus_min is not None else []),
        "## Done",
        *(_done_line(legend, t, _partner(t, side, titles)) for t in done),
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


def _partner(trial: Trial, side: Mapping[str, Beside], titles: Mapping[str, str]) -> str | None:
    """The marker's tail: the partner's title ("" if unknown), or None when nothing ran beside."""
    if trial.id not in side:
        return None
    partner = side[trial.id].partner_id
    return titles.get(partner, "") if partner is not None else ""
