from pathlib import Path

from scrolly.clock import FixedClock
from scrolly.domain.merge import ImportBatch
from scrolly.domain.models import TrialState
from scrolly.io.importers import parse_upload
from scrolly.ports import Store
from scrolly.services.importing import ImportService

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _batch(name: str) -> ImportBatch:
    return parse_upload(name, (FIXTURES / name).read_bytes())


def test_the_prototype_backup_lands_in_all_four_tables(store: Store, clock: FixedClock) -> None:
    summary = ImportService(store, clock).merge(_batch("prototype_backup.json"))
    assert (summary.trials_added, summary.horizon_added, summary.arts_added) == (7, 2, 3)
    assert summary.horizon_skipped == 1  # the duplicate Mandate
    assert len(store.trials.list_all()) == 7
    assert len(store.arts.list_all()) == 3


def test_importing_twice_changes_nothing(store: Store, clock: FixedClock) -> None:
    service = ImportService(store, clock)
    service.merge(_batch("prototype_backup.json"))
    before = (store.trials.list_all(), store.horizon.list_all(), store.days.list_all())
    again = service.merge(_batch("prototype_backup.json"))
    assert again.added == 0 and again.skipped == 13
    assert (store.trials.list_all(), store.horizon.list_all(), store.days.list_all()) == before


def test_open_trials_from_past_days_are_settled_after_import(
    store: Store, clock: FixedClock
) -> None:
    ImportService(store, clock).merge(_batch("prototype_backup.json"))
    states = {t.title: t.state for t in store.trials.list_all()}
    assert states["Write report"] is TrialState.IMMEDIATE  # today's trials stay open
    assert states["Tidy desk"] is TrialState.REMAINING
    assert states["Call plumber"] is TrialState.POSTPONED


def test_the_discord_board_recovers_conquered_days_and_counts_them(
    store: Store, clock: FixedClock
) -> None:
    ImportService(store, clock).merge(_batch("quest_board.md"))
    sealed = [d.logical_day.isoformat() for d in store.days.list_all() if d.first_sealed_at]
    assert sealed == ["2026-10-14", "2026-10-16"]
    assert all(t.state is TrialState.DONE for t in store.trials.list_all())


def test_discord_recovery_skips_days_the_json_already_has(store: Store, clock: FixedClock) -> None:
    service = ImportService(store, clock)
    service.merge(_batch("prototype_backup.json"))
    overlap = (
        b"# Quest Board\n07/10/2026\n## Done\n"
        b":green_apple: :white_circle: feed the CAT (10m) >> 10m\n"
    )
    summary = service.merge(parse_upload("overlap.md", overlap))
    assert (summary.trials_added, summary.trials_skipped) == (0, 1)
    service.merge(_batch("quest_board.md"))
    assert len(store.trials.list_all()) == 7 + 6
