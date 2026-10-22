"""The Secret Seal Inscription: words typed in Settings that do something unusual. Pure."""

import re
from dataclasses import dataclass
from enum import StrEnum

from scrolly.domain.victory import Scene

ARISE_DAY = 100
MAX_DAY = 9999


class SealKind(StrEnum):
    DUSK = "dusk"  # force dusk for the day: the palette, the chime and the poem
    SUNRISE = "sunrise"  # clear the forced dusk
    DAY = "day"  # the milestone overlay for a day number
    ROLLOVER = "4am"  # run today's rollover now
    RESTART = "restart-today"  # today starts over at the zero state
    CEREMONY = "ceremony"  # show the finished-day ceremony once, as a preview; nothing changes


@dataclass(frozen=True)
class Seal:
    kind: SealKind
    day: int | None = None  # only for SealKind.DAY
    scene: Scene | None = None  # only for SealKind.CEREMONY


_WORDS = {
    "dusk": Seal(SealKind.DUSK),
    "sunrise": Seal(SealKind.SUNRISE),
    "4am": Seal(SealKind.ROLLOVER),
    "restart-today": Seal(SealKind.RESTART),
    "tribulation": Seal(SealKind.CEREMONY, scene=Scene.THUNDER),
    "another day": Seal(SealKind.CEREMONY, scene=Scene.WIND),
    "arise": Seal(SealKind.DAY, ARISE_DAY),
}
_DAY = re.compile(r"(?:day\s+)?([0-9]{1,4})")
# Marks around the words, never inside them: sentence marks, quotes, brackets.
# "-" is left alone, so "-3" and "restart-today" stay as they are.
_MARKS = " .,;:!?…\"'“”()[]"


def parse_seal(text: str) -> Seal | None:
    """The seal these words name, or None. Case, extra spaces and marks around them are ignored."""
    cleaned = " ".join(text.split()).strip(_MARKS).casefold()
    if cleaned in _WORDS:
        return _WORDS[cleaned]
    match = _DAY.fullmatch(cleaned)
    if match is not None and 1 <= int(match[1]) <= MAX_DAY:
        return Seal(SealKind.DAY, int(match[1]))
    return None
