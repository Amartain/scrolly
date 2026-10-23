"""Knowledge of the Dao through the API."""

from typing import Any

from fastapi.testclient import TestClient

from scrolly.domain.knowledge import KEYS


def _knowledge(client: TestClient) -> dict[str, Any]:
    known: dict[str, Any] = client.get("/api/view").json()["knowledge"]
    return known


def test_a_newcomer_has_learned_nothing_and_the_whole_walk_ahead(client: TestClient) -> None:
    known = _knowledge(client)
    assert (known["count"], known["total"]) == (0, len(KEYS))
    assert known["pending_steps"][0] == "dump"
    assert (known["tour"], known["bar_hidden"], known["complete"]) == (True, False, False)


def test_learning_is_kept_and_a_wrong_lesson_refused(client: TestClient) -> None:
    learned = client.post("/api/knowledge/learn", json={"key": "open"}).json()
    assert learned["learned"] == ["open"]  # only the knowledge comes back
    assert client.post("/api/knowledge/learn", json={"key": "nope"}).status_code == 422
    assert _knowledge(client)["count"] == 1


def test_the_bar_can_be_hidden_and_the_tour_turned_off(client: TestClient) -> None:
    client.put("/api/knowledge", json={"bar_hidden": True})
    client.put("/api/knowledge", json={"tour": False})
    known = _knowledge(client)
    assert (known["bar_hidden"], known["tour"], known["pending_steps"]) == (True, False, [])


def test_enlightenment_waits_for_everything_then_is_kept(client: TestClient) -> None:
    assert client.post("/api/knowledge/enlightened").status_code == 422
    for key in KEYS:
        client.post("/api/knowledge/learn", json={"key": key})
    assert _knowledge(client)["complete"] is True
    client.post("/api/knowledge/enlightened")
    assert _knowledge(client)["enlightened"] is True
