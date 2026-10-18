from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scrolly.api.app import create_app
from scrolly.clock import FixedClock
from scrolly.ports import Store
from scrolly.storage.migrate import upgrade_to_head
from scrolly.storage.store import SqliteStores, make_engine


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime.fromisoformat("2026-10-18T13:12:00+02:00"))


@pytest.fixture
def stores(tmp_path: Path) -> SqliteStores:
    db_file = tmp_path / "scrolly.db"
    upgrade_to_head(db_file, tmp_path / "backups")
    return SqliteStores(make_engine(db_file))


@pytest.fixture
def store(stores: SqliteStores) -> Iterator[Store]:
    with stores() as opened:
        yield opened


@pytest.fixture
def client(clock: FixedClock, stores: SqliteStores) -> TestClient:
    @contextmanager
    def factory() -> Iterator[Store]:
        with stores() as opened:
            yield opened

    return TestClient(create_app(clock, factory))
