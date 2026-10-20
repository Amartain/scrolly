from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scrolly.api.app import create_app
from scrolly.clock import FixedClock
from scrolly.ports import Store
from scrolly.storage.store import SqliteStores


@pytest.fixture
def copies(tmp_path: Path) -> Path:
    """Where the app keeps a copy of the data before a restore replaces it."""
    return tmp_path / "backups"


@pytest.fixture
def app_client(clock: FixedClock, stores: SqliteStores, copies: Path) -> TestClient:
    """Like `client`, but with a data folder for the files kept beside the database."""

    @contextmanager
    def factory() -> Iterator[Store]:
        with stores() as opened:
            yield opened

    return TestClient(create_app(clock, factory, data_dir=copies.parent))
