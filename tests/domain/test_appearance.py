from datetime import datetime

from scrolly.domain.appearance import DayVariant, Phase, Preferences, Theme, resolve_appearance

NOW = datetime.fromisoformat("2026-10-18T13:12:00+02:00")


def test_defaults_are_serene_by_day() -> None:
    result = resolve_appearance(Preferences(), NOW)
    assert (result.theme, result.day_variant, result.phase) == (Theme.SERENE, None, Phase.DAY)


def test_pavilion_keeps_its_variant() -> None:
    prefs = Preferences(theme=Theme.PAVILION, day_variant=DayVariant.CRIMSON)
    assert resolve_appearance(prefs, NOW).day_variant is DayVariant.CRIMSON


def test_serene_ignores_the_variant() -> None:
    prefs = Preferences(theme=Theme.SERENE, day_variant=DayVariant.CRIMSON)
    assert resolve_appearance(prefs, NOW).day_variant is None
