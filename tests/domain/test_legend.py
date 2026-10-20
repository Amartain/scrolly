import pytest

from scrolly.domain.legend import (
    DEFAULT_LEGEND,
    STATE_SYMBOLS,
    TYPE_SYMBOLS,
    LegendError,
    TrialType,
    build_legend,
    parse_emoji,
    parse_shortcode,
    type_of,
    with_symbol,
)
from scrolly.domain.models import ArtKind, TrialState


@pytest.mark.parametrize(
    ("is_mandate", "art_kind", "expected"),
    [
        (True, None, TrialType.MANDATE),
        (False, None, TrialType.MORTAL),
        (False, ArtKind.FOUNDATIONAL, TrialType.FOUNDATIONAL),
        (False, ArtKind.RESTORATIVE, TrialType.RESTORATIVE),
        (True, ArtKind.FOUNDATIONAL, TrialType.FOUNDATIONAL),
    ],
)
def test_type_of(is_mandate: bool, art_kind: ArtKind | None, expected: TrialType) -> None:
    assert type_of(is_mandate, art_kind) is expected


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


def test_a_custom_symbol_is_laid_over_the_default() -> None:
    mine = with_symbol({}, "states", "done", "🌱", "seedling")
    legend = build_legend(mine)
    assert (legend.states[TrialState.DONE].emoji, legend.states[TrialState.DONE].shortcode) == (
        "🌱",
        ":seedling:",
    )
    assert legend.states[TrialState.DONE].label == "Conquered"
    assert legend.states[TrialState.IMMEDIATE] == STATE_SYMBOLS[TrialState.IMMEDIATE]


def test_giving_only_the_emoji_keeps_the_shortcode_and_the_other_way_round() -> None:
    legend = build_legend(with_symbol({}, "types", "mandate", "👑", None))
    assert (legend.types[TrialType.MANDATE].emoji, legend.types[TrialType.MANDATE].shortcode) == (
        "👑",
        ":lotus:",
    )
    legend = build_legend(with_symbol({}, "types", "mandate", None, ":crown:"))
    assert legend.types[TrialType.MANDATE].emoji == "🪷"
    assert legend.types[TrialType.MANDATE].shortcode == ":crown:"


def test_neither_emoji_nor_shortcode_restores_the_default() -> None:
    mine = with_symbol({}, "states", "done", "🌱", ":seedling:")
    assert build_legend(with_symbol(mine, "states", "done", None, None)) == DEFAULT_LEGEND


def test_no_two_symbols_may_share_an_emoji_or_a_shortcode() -> None:
    with pytest.raises(LegendError, match="Conquered"):
        with_symbol({}, "states", "immediate", "🍃", None)
    with pytest.raises(LegendError, match="Heavenly Mandate"):
        with_symbol({}, "types", "mortal", None, ":LOTUS:")


@pytest.mark.parametrize("shortcode", ["", "two words", ":a:b:", "x" * 40])
def test_unreadable_shortcodes_are_refused(shortcode: str) -> None:
    with pytest.raises(LegendError, match="shortcode"):
        parse_shortcode(shortcode)


@pytest.mark.parametrize("emoji", ["", "two emoji", "x" * 20])
def test_unreadable_symbols_are_refused(emoji: str) -> None:
    with pytest.raises(LegendError, match="emoji"):
        parse_emoji(emoji)


def test_only_known_symbols_can_be_changed() -> None:
    with pytest.raises(LegendError):
        with_symbol({}, "states", "nonsense", "🌱", None)
    with pytest.raises(LegendError):
        with_symbol({}, "weather", "done", "🌱", None)
