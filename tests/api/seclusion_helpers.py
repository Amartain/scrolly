"""Small helpers for tests that drive the focus room through the API."""

from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def seal(client: TestClient, *titles: str) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")


def room(client: TestClient) -> dict[str, Any]:
    state: dict[str, Any] = client.get("/api/seclusion").json()
    return state


def enter_on(client: TestClient, discipline: str, *titles: str) -> None:
    seal(client, *titles)
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/discipline", json={"discipline": discipline})


def later(clock: FixedClock, minutes: float) -> None:
    clock.set(clock.now() + timedelta(minutes=minutes))


def logged(client: TestClient) -> int:
    """Seconds logged on the trial at hand."""
    return int(room(client)["trial"]["timer"]["elapsed_s"])
