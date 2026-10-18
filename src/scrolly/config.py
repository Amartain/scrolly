import os
from pathlib import Path

DEFAULT_PORT = 4747
REALM_DEFAULT = "daily"


def data_dir() -> Path:
    """Where the database, backups and the instance file live."""
    override = os.environ.get("SCROLLY_HOME")
    path = Path(override) if override else Path.home() / ".scrolly"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "scrolly.db"
