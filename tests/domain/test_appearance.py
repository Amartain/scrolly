import pytest

from scrolly.domain.appearance import (
    AppearanceError,
    DayVariant,
    Phase,
    Preferences,
    Theme,
    choose_theme,
    resolve_appearance,
)


def test_defaults_are_serene_by_day_in_scroll_colours() -> None:
    result = resolve_appearance(Preferences())
    assert (result.theme, result.day_variant, result.phase) == (
        Theme.SERENE,
        DayVariant.SCROLL,
        Phase.DAY,
    )


def test_the_phase_comes_from_the_sunset_system() -> None:
    assert resolve_appearance(Preferences(), Phase.DUSK).phase is Phase.DUSK


def test_pavilion_keeps_its_variant() -> None:
    prefs = Preferences(theme=Theme.PAVILION, day_variant=DayVariant.CRIMSON)
    assert resolve_appearance(prefs).day_variant is DayVariant.CRIMSON


def test_serene_shows_its_own_variant_not_pavilions() -> None:
    prefs = Preferences(
        theme=Theme.SERENE, day_variant=DayVariant.CRIMSON, serene_variant=DayVariant.GREEN
    )
    assert resolve_appearance(prefs).day_variant is DayVariant.GREEN


def test_each_theme_keeps_its_own_variant() -> None:
    green = choose_theme(Preferences(), Theme.SERENE, DayVariant.GREEN)
    crimson = choose_theme(green, Theme.PAVILION, DayVariant.CRIMSON)
    back = choose_theme(crimson, Theme.SERENE, None)
    assert resolve_appearance(back).day_variant is DayVariant.GREEN
    assert choose_theme(back, Theme.PAVILION, None).day_variant is DayVariant.CRIMSON


def test_a_variant_of_the_other_theme_is_refused() -> None:
    with pytest.raises(AppearanceError):
        choose_theme(Preferences(), Theme.SERENE, DayVariant.TEAL)
    with pytest.raises(AppearanceError):
        choose_theme(Preferences(), Theme.PAVILION, DayVariant.GREEN)
