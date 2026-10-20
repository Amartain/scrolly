from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from scrolly.api.app import create_app
from scrolly.clock import FixedClock
from scrolly.ports import Store
from scrolly.storage.store import SqliteStores


@pytest.fixture
def copies(tmp_path: Path) -> Path:
    return tmp_path / "copies"


@pytest.fixture
def app_client(clock: FixedClock, stores: SqliteStores, copies: Path) -> TestClient:
    @contextmanager
    def factory() -> Iterator[Store]:
        with stores() as opened:
            yield opened

    return TestClient(create_app(clock, factory, backup_dir=copies))


def _seal(client: TestClient, *titles: str) -> dict[str, Any]:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    sealed: dict[str, Any] = client.post("/api/planning/seal").json()
    return sealed


def _upload(client: TestClient, name: str, content: bytes) -> Any:
    return client.post("/api/import", files={"file": (name, content, "application/octet-stream")})


def _titles(client: TestClient) -> list[str]:
    view = client.get("/api/view").json()
    return sorted(t["title"] for t in view["planning"]["trials"])


def test_backup_purge_restore_brings_the_trials_back(app_client: TestClient, copies: Path) -> None:
    _seal(app_client, "Write", "Tidy")
    backup = app_client.get("/api/export").content

    purged = app_client.post("/api/purge").json()
    assert purged["planning"]["trials"] == []

    reply = _upload(app_client, "scrolly-backup.zip", backup)
    assert reply.status_code == 200 and reply.json()["added"] > 0
    assert _titles(app_client) == ["Tidy", "Write"]
    # A copy of what was there (the purged data) is kept first.
    assert len(list(copies.glob("scrolly-before-restore-*.zip"))) == 1


def test_restoring_a_zip_replaces_what_is_there(app_client: TestClient) -> None:
    _seal(app_client, "Old one")
    empty_backup = app_client.get("/api/export").content
    app_client.post("/api/purge")
    app_client.post("/api/trials", json={"title": "Added after the backup"})
    _upload(app_client, "b.zip", empty_backup)
    assert "Added after the backup" not in _titles(app_client)


def test_a_bad_zip_is_refused_and_nothing_changes(app_client: TestClient, copies: Path) -> None:
    _seal(app_client, "Keep me")
    reply = _upload(app_client, "broken.zip", b"not a zip")
    assert reply.status_code == 422 and "zip" in reply.json()["detail"]
    assert _titles(app_client) == ["Keep me"]
    assert not copies.exists()


def test_a_zip_with_an_unknown_table_is_refused_before_anything_is_replaced(
    app_client: TestClient,
) -> None:
    import io
    import zipfile

    _seal(app_client, "Keep me")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("trial.csv", "id\n")
        z.writestr("mystery.csv", "id\n1\n")
    reply = _upload(app_client, "odd.zip", buffer.getvalue())
    assert reply.status_code == 422 and "mystery" in reply.json()["detail"]
    assert _titles(app_client) == ["Keep me"]


def test_a_single_csv_adds_only_new_rows(app_client: TestClient) -> None:
    _seal(app_client, "Write")
    horizon_csv = (
        "id,title,is_mandate,position,origin_type,created_at,updated_at\n"
        "h1,A fresh idea,false,0,brain_dump,2026-10-18T09:00:00+02:00,2026-10-18T09:00:00+02:00\n"
    )
    first = _upload(app_client, "horizon_item.csv", horizon_csv.encode()).json()
    assert (first["added"], first["skipped"]) == (1, 0)
    second = _upload(app_client, "horizon_item.csv", horizon_csv.encode()).json()
    assert (second["added"], second["skipped"]) == (0, 1)
    horizon = app_client.get("/api/view").json()["planning"]["horizon"]
    assert [h["title"] for h in horizon] == ["A fresh idea"]


def test_purge_keeps_conquered_trials_and_sends_mandates_back(app_client: TestClient) -> None:
    sealed = _seal(app_client, "Done one", "Mandate", "Chore")
    first = sealed["dashboard"]["immediate"]["id"]
    app_client.post(f"/api/trials/{first}/conquer")
    view = app_client.get("/api/view").json()
    mandate = next(t for t in view["planning"]["trials"] if t["title"] == "Mandate")
    app_client.patch(f"/api/trials/{mandate['id']}", json={"is_mandate": True})

    after = app_client.post("/api/purge").json()
    assert after["planning"]["trials"] == []
    assert [c["title"] for c in after["dashboard"]["conquered"]] == ["Done one"]
    assert [h["title"] for h in after["planning"]["horizon"]] == ["Mandate"]
    assert after["dashboard"]["heavenly_cycles"] == 1


def test_purging_the_planning_in_progress_returns_to_the_zero_state(
    app_client: TestClient,
) -> None:
    app_client.post("/api/planning/start")
    app_client.put("/api/planning/text", json={"text": "Draft line"})
    app_client.post("/api/planning/proceed")
    after = app_client.post("/api/purge").json()
    assert after["planning"]["status"] == "zero" and after["planning"]["trials"] == []
