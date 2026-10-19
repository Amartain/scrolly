"""Discord Dispatch markdown (the Scroll of Heavenly Tribulations, formerly the Quest Board).

Only Done lines carry time, so only they are read."""

import re
from datetime import date

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
# A stray character before the title (a BOM, a pasted "=") is tolerated. The title is the current
# "Scroll of Heavenly Tribulations and Ascendent Trials" (a shortcode may come first), or the old
# "Quest Board".
_BOARD = re.compile(
    r"(?m)^[^\w\r\n]*#\s*(?::\w+:\s*)?"
    r"(?:Quest Board|Scroll of Heavenly Tribulations and Ascend[ea]nt Trials)[^\n]*$"
)
_DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_SHORTCODE = re.compile(r":(\w+):\s*(.*)")
_DONE_LINE = re.compile(r"(.+?)\s*\(([^()]*)\)\s*>>\s*(\S+)")
# Old boards wrote "45m", "1h", "1.5h", "1h15m" or bare minutes; imports read more than the form.
_OLD_TIME = re.compile(r"(?:([0-9]+(?:\.[0-9]+)?)h)?(?:([0-9]+)m)?")


def _minutes(text: str) -> int | None:
    cleaned = "".join(text.split()).lower()
    if not cleaned:
        return None
    if re.fullmatch(r"[0-9]+", cleaned):
        return int(cleaned)
    match = _OLD_TIME.fullmatch(cleaned)
    if match is None or not any(match.groups()):
        raise ValueError(text)
    hours, minutes = match.groups()
    return round(float(hours or 0) * 60) + int(minutes or 0)


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
        expected_min, actual_min = _minutes(expected), _minutes(actual)
    except ValueError:
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
        raise ImportFormatError("No Scroll of Heavenly Tribulations (or Quest Board) in this file")
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
