from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import Response

from scrolly.clock import FixedClock

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _upload(client: TestClient, name: str, content: bytes | None = None) -> Response:
    data = (FIXTURES / name).read_bytes() if content is None else content
    reply: Response = client.post("/api/import", files={"file": (name, data)})
    return reply


def test_importing_the_prototype_backup_reports_what_was_added(client: TestClient) -> None:
    reply = _upload(client, "prototype_backup.json")
    assert reply.status_code == 200
    body = reply.json()
    assert (body["trials_added"], body["horizon_added"], body["arts_added"]) == (7, 2, 3)
    assert body["added"] == 12 and body["skipped"] == 1
    assert body["view"]["appearance"]["theme"] == "serene"


def test_a_second_import_adds_nothing(client: TestClient) -> None:
    _upload(client, "prototype_backup.json")
    body = _upload(client, "prototype_backup.json").json()
    assert body["added"] == 0 and body["skipped"] == 13


def test_discord_markdown_is_accepted(client: TestClient) -> None:
    body = _upload(client, "quest_board.md").json()
    assert body["trials_added"] == 6


def test_an_unknown_file_type_is_a_plain_422(client: TestClient) -> None:
    reply = _upload(client, "notes.txt", b"hello")
    assert reply.status_code == 422
    assert ".json" in reply.json()["detail"]


def test_broken_json_is_a_plain_422(client: TestClient) -> None:
    reply = _upload(client, "backup.json", b"{nope")
    assert reply.status_code == 422


def test_the_view_rolls_the_previous_day_over_once_the_clock_moves(
    client: TestClient, clock: FixedClock
) -> None:
    _upload(client, "prototype_backup.json")
    clock.set(datetime.fromisoformat("2026-10-19T04:00:00+02:00"))
    assert client.get("/api/view").status_code == 200
    assert client.get("/api/view").status_code == 200
