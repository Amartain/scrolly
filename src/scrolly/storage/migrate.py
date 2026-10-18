import shutil
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

MIGRATIONS = Path(__file__).parent / "migrations"


def _config(db_file: Path) -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_file}")
    return config


def _is_behind(db_file: Path, config: Config) -> bool:
    head = ScriptDirectory.from_config(config).get_current_head()
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        with engine.connect() as connection:
            return MigrationContext.configure(connection).get_current_revision() != head
    finally:
        engine.dispose()


def upgrade_to_head(db_file: Path, backup_dir: Path) -> Path | None:
    """Bring the database up to date. Returns the backup path if one was made.

    A copy of an existing, non-empty database is kept before any migration runs.
    """
    config = _config(db_file)
    backup: Path | None = None
    if db_file.exists() and db_file.stat().st_size > 0 and _is_behind(db_file, config):
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = backup_dir / f"scrolly-{stamp}.db"
        shutil.copy2(db_file, backup)
    command.upgrade(config, "head")
    return backup
