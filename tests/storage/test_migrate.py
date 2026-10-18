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
