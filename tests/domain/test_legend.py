import pytest

from scrolly.domain.legend import STATE_SYMBOLS, TYPE_SYMBOLS, TrialType, type_of
from scrolly.domain.models import OriginType, TrialState


@pytest.mark.parametrize(
    ("is_mandate", "origin", "expected"),
    [
        (True, OriginType.BRAIN_DUMP, TrialType.MANDATE),
        (False, OriginType.BRAIN_DUMP, TrialType.MORTAL),
        (True, OriginType.HORIZON, TrialType.MANDATE),
        (False, OriginType.QUICK_ADD, TrialType.MORTAL),
        (False, OriginType.FOUNDATIONAL_ART, TrialType.FOUNDATIONAL),
        (False, OriginType.RESTORATIVE_ART, TrialType.RESTORATIVE),
        (True, OriginType.FOUNDATIONAL_ART, TrialType.FOUNDATIONAL),
    ],
)
def test_type_of(is_mandate: bool, origin: OriginType, expected: TrialType) -> None:
    assert type_of(is_mandate, origin) is expected


def test_the_legend_of_the_scrolls() -> None:
    shortcodes = {s: sym.shortcode for s, sym in STATE_SYMBOLS.items()}
    assert shortcodes[TrialState.DONE] == ":leaves:"
    assert shortcodes[TrialState.IMMEDIATE] == ":droplet:"
    assert shortcodes[TrialState.REMAINING] == ":cloud:"
    assert shortcodes[TrialState.POSTPONED] == ":zzz:"
    assert {t: sym.shortcode for t, sym in TYPE_SYMBOLS.items()} == {
        TrialType.MANDATE: ":lotus:",
        TrialType.MORTAL: ":white_circle:",
        TrialType.FOUNDATIONAL: ":scroll:",
        TrialType.RESTORATIVE: ":herb:",
    }


def test_every_type_has_a_symbol_and_no_symbol_repeats() -> None:
    assert set(TYPE_SYMBOLS) == set(TrialType)
    emoji = [s.emoji for s in (*STATE_SYMBOLS.values(), *TYPE_SYMBOLS.values())]
    assert len(emoji) == len(set(emoji))
