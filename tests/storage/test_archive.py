from datetime import datetime
from pathlib import Path

import pytest

from scrolly.domain.archive import ArchiveError, Table
from scrolly.domain.models import Day, HorizonItem, Trial, TrialState
from scrolly.ports import Store
from scrolly.storage.migrate import upgrade_to_head
from scrolly.storage.store import SqliteStores, make_engine

NOW = datetime.fromisoformat("2026-10-18T13:12:00+02:00")
TITLE = 'Write, "the" report\n日落'


def _fill(store: Store) -> None:
    sealed = datetime.fromisoformat("2026-10-18T09:00:00+02:00")
    store.trials.save(
        [
            Trial(
                id="t1",
                logical_day=NOW.date(),
                title=TITLE,
                state=TrialState.DONE,
                is_mandate=True,
                essence_expected_min=45,
                completed_at=NOW,
                timer_accumulated_s=61,
            )
        ],
        NOW,
    )
    store.horizon.replace_all([HorizonItem(id="h1", title="Idea", worked_s=300)], NOW)
    store.days.save(Day(logical_day=NOW.date(), first_sealed_at=sealed), NOW)
    store.settings.set("sunset", {"hour": 21}, NOW)
    store.commit()


def test_dump_then_replace_into_another_database_gives_the_same_data(
    store: Store, tmp_path: Path
) -> None:
    _fill(store)
    tables = store.archive.dump()
    assert tables["trial"].rows[0]["is_mandate"] == "true"
    assert tables["trial"].rows[0]["essence_actual_min"] is None

    other_dir = tmp_path / "other"
    other_dir.mkdir()
    upgrade_to_head(other_dir / "scrolly.db", other_dir / "backups")
    with SqliteStores(make_engine(other_dir / "scrolly.db"))() as other:
        assert other.archive.replace_all(tables) == sum(len(t.rows) for t in tables.values())
        assert other.archive.dump() == tables
        trial = other.trials.list_all()[0]
        assert (trial.title, trial.is_mandate, trial.timer_accumulated_s) == (TITLE, True, 61)
        assert other.horizon.list_all()[0].worked_s == 300


def test_replace_removes_what_was_there(store: Store) -> None:
    _fill(store)
    empty = {name: Table(t.columns, []) for name, t in store.archive.dump().items()}
    store.archive.replace_all(empty)
    assert store.trials.list_all() == [] and store.horizon.list_all() == []


def test_a_bad_file_changes_nothing(store: Store) -> None:
    _fill(store)
    before = store.archive.dump()
    for tables in (
        {"nonsense": Table(("id",), [])},
        {"trial": Table(("id", "colour"), [{"id": "x", "colour": "red"}])},
        {"trial": Table(("id", "is_mandate"), [{"id": "x", "is_mandate": "maybe"}])},
    ):
        with pytest.raises(ArchiveError):
            store.archive.replace_all(tables)
    assert store.archive.dump() == before


def test_missing_columns_take_their_defaults_so_older_backups_restore(store: Store) -> None:
    stamp = "2026-10-18T09:00:00+02:00"
    row: dict[str, str | None] = {
        "id": "t9",
        "created_at": stamp,
        "updated_at": stamp,
        "logical_day": "2026-10-18",
        "title": "Old backup",
        "state": "done",
        "origin_type": "brain_dump",
    }
    store.archive.replace_all({"trial": Table(tuple(row), [row])})
    trial = store.trials.list_all()[0]
    assert (trial.title, trial.is_mandate, trial.timer_accumulated_s, trial.art_kind) == (
        "Old backup",
        False,
        0,
        None,
    )


def test_adding_a_table_skips_rows_that_are_already_there(store: Store) -> None:
    _fill(store)
    table = store.archive.dump()["horizon_item"]
    second = dict(table.rows[0], id="h2", title="Second idea")
    both = Table(table.columns, [table.rows[0], second])
    assert store.archive.add_missing({"horizon_item": both}) == (1, 1)
    assert [i.title for i in store.horizon.list_all()] == ["Idea", "Second idea"]
