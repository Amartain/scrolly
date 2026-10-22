from pathlib import Path

from alembic import command
from sqlalchemy import create_engine, text

from scrolly.storage.migrate import _config, upgrade_to_head


def test_fresh_database_reaches_head_without_backup(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    assert upgrade_to_head(db_file, tmp_path / "backups") is None
    assert db_file.stat().st_size > 0


def test_up_to_date_database_is_not_backed_up(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    upgrade_to_head(db_file, tmp_path / "backups")
    assert upgrade_to_head(db_file, tmp_path / "backups") is None
    assert not (tmp_path / "backups").exists()


def test_pending_revisions_are_backed_up_first(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    upgrade_to_head(db_file, tmp_path / "backups")
    command.downgrade(_config(db_file), "base")
    backup = upgrade_to_head(db_file, tmp_path / "backups")
    assert backup is not None and backup.exists()


def test_upgrading_from_the_first_revision_keeps_settings(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0001")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO setting (id, realm_id, key, value_json, created_at, updated_at) "
                "VALUES ('s1', 'daily', 'appearance', '{\"theme\": \"pavilion\"}', 'now', 'now')"
            )
        )
    backup = upgrade_to_head(db_file, tmp_path / "backups")
    assert backup is not None
    with engine.connect() as connection:
        kept = connection.execute(text("SELECT value_json FROM setting WHERE key = 'appearance'"))
        assert kept.scalar_one() == '{"theme": "pavilion"}'
        tables = {row[0] for row in connection.execute(text("SELECT name FROM sqlite_master"))}
    assert {"trial", "horizon_item", "art", "day"} <= tables
    engine.dispose()


def test_the_planning_draft_table_exists_after_upgrading(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    upgrade_to_head(db_file, tmp_path / "backups")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.connect() as connection:
        tables = {row[0] for row in connection.execute(text("SELECT name FROM sqlite_master"))}
    engine.dispose()
    assert "planning_draft" in tables


def test_qi_actual_is_added_to_trials_without_touching_existing_rows(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0004")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO trial (id, realm_id, created_at, updated_at, logical_day, title,"
                " state,"
                " is_mandate, origin_type, position, note, timer_accumulated_s, qi_expected)"
                " VALUES ('t1', 'daily', 'now', 'now', '2026-10-18', 'Old', 'done', 0,"
                " 'brain_dump', 0, '', 0, 40)"
            )
        )
    upgrade_to_head(db_file, tmp_path / "backups")
    with engine.connect() as connection:
        row = connection.execute(text("SELECT qi_expected, qi_actual FROM trial")).one()
    engine.dispose()
    assert tuple(row) == (40, None)


def test_horizon_items_get_zero_worked_time_on_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0006")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO horizon_item (id, realm_id, created_at, updated_at, title,"
                " is_mandate, note, position, origin_type)"
                " VALUES ('h1', 'daily', 'now', 'now', 'Old idea', 0, '', 0, 'brain_dump')"
            )
        )
    upgrade_to_head(db_file, tmp_path / "backups")
    with engine.connect() as connection:
        worked = connection.execute(text("SELECT worked_s FROM horizon_item")).scalar_one()
    engine.dispose()
    assert worked == 0


def test_art_kind_is_backfilled_for_rows_that_came_from_an_art(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0005")
    engine = create_engine(f"sqlite:///{db_file}")
    insert = (
        "INSERT INTO trial (id, realm_id, created_at, updated_at, logical_day, title, state,"
        " is_mandate, origin_type, position, note, timer_accumulated_s)"
        " VALUES ('{id}', 'daily', 'now', 'now', '2026-10-18', 'T', 'done', 0,"
        " '{origin}', 0, '', 0)"
    )
    with engine.begin() as connection:
        for trial_id, origin in (
            ("a", "foundational_art"),
            ("b", "restorative_art"),
            ("c", "horizon"),
        ):
            connection.execute(text(insert.format(id=trial_id, origin=origin)))
    upgrade_to_head(db_file, tmp_path / "backups")
    with engine.connect() as connection:
        rows = connection.execute(text("SELECT id, art_kind FROM trial ORDER BY id")).all()
    engine.dispose()
    assert [tuple(r) for r in rows] == [("a", "foundational"), ("b", "restorative"), ("c", None)]


def test_days_get_a_poem_shown_column_on_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0007")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO day (id, realm_id, created_at, updated_at, logical_day,"
                " advisor_silenced) VALUES ('d1', 'daily', 'now', 'now', '2026-10-18', 0)"
            )
        )
    upgrade_to_head(db_file, tmp_path / "backups")
    with engine.connect() as connection:
        shown = connection.execute(text("SELECT poem_shown_at FROM day")).scalar_one()
    engine.dispose()
    assert shown is None


def test_days_get_a_victory_seen_column_on_upgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "scrolly.db"
    command.upgrade(_config(db_file), "0011")
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO day (id, realm_id, created_at, updated_at, logical_day,"
                " advisor_silenced) VALUES ('d1', 'daily', 'now', 'now', '2026-10-18', 0)"
            )
        )
    upgrade_to_head(db_file, tmp_path / "backups")
    with engine.connect() as connection:
        seen = connection.execute(text("SELECT victory_seen_at FROM day")).scalar_one()
    engine.dispose()
    assert seen is None
