from scrolly.domain.appearance import DayVariant, Phase, Preferences, Theme, resolve_appearance


def test_defaults_are_serene_by_day() -> None:
    result = resolve_appearance(Preferences())
    assert (result.theme, result.day_variant, result.phase) == (Theme.SERENE, None, Phase.DAY)


def test_the_phase_comes_from_the_sunset_system() -> None:
    assert resolve_appearance(Preferences(), Phase.DUSK).phase is Phase.DUSK


def test_pavilion_keeps_its_variant() -> None:
    prefs = Preferences(theme=Theme.PAVILION, day_variant=DayVariant.CRIMSON)
    assert resolve_appearance(prefs).day_variant is DayVariant.CRIMSON


def test_serene_ignores_the_variant() -> None:
    prefs = Preferences(theme=Theme.SERENE, day_variant=DayVariant.CRIMSON)
    assert resolve_appearance(prefs).day_variant is None
