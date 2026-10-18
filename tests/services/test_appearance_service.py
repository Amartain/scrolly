from scrolly.clock import FixedClock
from scrolly.domain.appearance import DayVariant, ReadingFont, Theme
from scrolly.ports import Store
from scrolly.services.appearance import KEY, AppearanceService
from scrolly.storage.store import SqliteStores


def test_choice_persists_across_stores(stores: SqliteStores, clock: FixedClock) -> None:
    with stores() as store:
        AppearanceService(store, clock).choose(Theme.PAVILION, DayVariant.CRIMSON)
    with stores() as later:
        prefs = AppearanceService(later, clock).preferences()
    assert (prefs.theme, prefs.day_variant) == (Theme.PAVILION, DayVariant.CRIMSON)


def test_choosing_without_variant_keeps_the_last_one(store: Store, clock: FixedClock) -> None:
    service = AppearanceService(store, clock)
    service.choose(Theme.PAVILION, DayVariant.CRIMSON)
    service.choose(Theme.SERENE, None)
    assert service.choose(Theme.PAVILION, None).day_variant is DayVariant.CRIMSON


def test_reading_font_defaults_to_atkinson(store: Store, clock: FixedClock) -> None:
    assert AppearanceService(store, clock).preferences().reading_font is ReadingFont.ATKINSON


def test_reading_font_choice_persists_across_stores(
    stores: SqliteStores, clock: FixedClock
) -> None:
    with stores() as store:
        AppearanceService(store, clock).choose_reading_font(ReadingFont.OPENDYSLEXIC)
    with stores() as later:
        prefs = AppearanceService(later, clock).preferences()
    assert prefs.reading_font is ReadingFont.OPENDYSLEXIC


def test_changing_theme_keeps_the_reading_font(store: Store, clock: FixedClock) -> None:
    service = AppearanceService(store, clock)
    service.choose_reading_font(ReadingFont.OPENDYSLEXIC)
    prefs = service.choose(Theme.PAVILION, DayVariant.CRIMSON)
    assert prefs.reading_font is ReadingFont.OPENDYSLEXIC


def test_changing_font_keeps_the_theme(store: Store, clock: FixedClock) -> None:
    service = AppearanceService(store, clock)
    service.choose(Theme.PAVILION, DayVariant.CRIMSON)
    prefs = service.choose_reading_font(ReadingFont.OPENDYSLEXIC)
    assert (prefs.theme, prefs.day_variant) == (Theme.PAVILION, DayVariant.CRIMSON)


def test_old_saved_appearance_without_a_font_reads_as_atkinson(
    store: Store, clock: FixedClock
) -> None:
    store.settings.set(KEY, {"theme": "pavilion", "day_variant": "teal"}, clock.now())
    prefs = AppearanceService(store, clock).preferences()
    assert (prefs.theme, prefs.reading_font) == (Theme.PAVILION, ReadingFont.ATKINSON)
