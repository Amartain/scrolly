from pathlib import Path

from alembic import command

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
