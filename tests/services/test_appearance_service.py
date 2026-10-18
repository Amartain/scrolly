from scrolly.clock import FixedClock
from scrolly.domain.appearance import DayVariant, Theme
from scrolly.ports import Store
from scrolly.services.appearance import AppearanceService
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
