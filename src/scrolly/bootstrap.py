from pathlib import Path

from fastapi import FastAPI

from scrolly.api.app import create_app
from scrolly.clock import SystemClock
from scrolly.config import data_dir, db_path
from scrolly.storage.migrate import upgrade_to_head
from scrolly.storage.store import SqliteStores, make_engine

STATIC_DIR = Path(__file__).parent / "static"


def build_app(with_static: bool = True) -> FastAPI:
    """Migrate the user's database and wire the real app."""
    upgrade_to_head(db_path(), data_dir() / "backups")
    stores = SqliteStores(make_engine(db_path()))
    return create_app(SystemClock(), stores, STATIC_DIR if with_static else None)
