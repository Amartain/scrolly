"""Discord Dispatch "Quest Board" markdown. Only Done lines carry time, so only they are read."""

import re
from datetime import date

from scrolly.domain.duration import DurationError, parse_duration
from scrolly.domain.merge import ImportBatch
from scrolly.domain.models import OriginType, Trial, TrialState
from scrolly.io.errors import ImportFormatError
from scrolly.io.ids import stable_id

# Type shortcodes are the same in the old and the new default sets.
_TYPES = {
    "lotus": (True, OriginType.BRAIN_DUMP),
    "white_circle": (False, OriginType.BRAIN_DUMP),
    "scroll": (False, OriginType.FOUNDATIONAL_ART),
    "herb": (False, OriginType.RESTORATIVE_ART),
}
# A stray character before "# Quest Board" (a BOM, a pasted "=") is tolerated.
_BOARD = re.compile(r"(?m)^[^\w\r\n]*#\s*Quest Board[^\n]*$")
_DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_SHORTCODE = re.compile(r":(\w+):\s*(.*)")
_DONE_LINE = re.compile(r"(.+?)\s*\(([^()]*)\)\s*>>\s*(\S+)")


def _done_lines(block: str) -> list[str]:
    lines: list[str] = []
    section = ""
    for line in block.splitlines():
        if line.startswith("##"):
            section = line.lstrip("# ").strip().lower()
        elif section == "done" and line.strip():
            lines.append(line.strip())
    return lines


def _trial(line: str, day: date, position: int) -> Trial | None:
    """One Done line: `:state: :type: title (expected) >> actual`. None if it does not fit."""
    state = _SHORTCODE.fullmatch(line)
    if state is None:
        return None
    rest = state.group(2)
    is_mandate, origin = False, OriginType.BRAIN_DUMP
    kind = _SHORTCODE.fullmatch(rest)
    if kind is not None and kind.group(1) in _TYPES:
        (is_mandate, origin), rest = _TYPES[kind.group(1)], kind.group(2)
    parts = _DONE_LINE.fullmatch(rest)
    if parts is None:
        return None
    title, expected, actual = parts.groups()
    try:
        expected_min, actual_min = parse_duration(expected), parse_duration(actual)
    except DurationError:
        return None
    return Trial(
        id=stable_id("discord", f"{day}:{position}:{title.casefold()}"),
        logical_day=day,
        title=title,
        state=TrialState.DONE,
        is_mandate=is_mandate,
        origin_type=origin,
        position=position,
        essence_expected_min=expected_min,
        essence_actual_min=actual_min,
    )


def _board_day(block: str) -> date | None:
    match = _DATE.search(block)
    if match is None:
        return None
    day, month, year = (int(part) for part in match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_discord_md(text: str, name: str = "") -> ImportBatch:
    blocks = _BOARD.split(text)[1:]
    if not blocks:
        raise ImportFormatError("No '# Quest Board' found in this file")
    trials: list[Trial] = []
    for block in blocks:
        day = _board_day(block)
        if day is None:
            continue
        for position, line in enumerate(_done_lines(block)):
            trial = _trial(line, day, position)
            if trial is not None:
                trials.append(trial)
    return ImportBatch(trials=trials)
