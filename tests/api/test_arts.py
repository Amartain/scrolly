from typing import Any

from fastapi.testclient import TestClient


def _arts(client: TestClient, kind: str = "foundational") -> list[dict[str, Any]]:
    arts: list[dict[str, Any]] = client.get("/api/view").json()["planning"][kind]
    return arts


def _add(client: TestClient, title: str, estimate: str = "", kind: str = "foundational") -> Any:
    return client.post("/api/arts", json={"kind": kind, "title": title, "estimate": estimate})


def test_an_art_is_added_edited_and_deleted(client: TestClient) -> None:
    assert _add(client, "Stretch", "10m").status_code == 200
    art = _arts(client)[0]
    assert (art["title"], art["expected_text"]) == ("Stretch", "10m")

    reply = client.patch(f"/api/arts/{art['id']}", json={"title": "Warm up", "estimate": "1h"})
    assert reply.status_code == 200
    art = _arts(client)[0]
    assert (art["title"], art["expected_text"]) == ("Warm up", "1h")

    assert client.delete(f"/api/arts/{art['id']}").status_code == 200
    assert _arts(client) == []


def test_a_duplicate_title_in_the_same_list_is_a_409(client: TestClient) -> None:
    _add(client, "Stretch")
    reply = _add(client, " stretch")
    assert reply.status_code == 409 and "already" in reply.json()["detail"].lower()
    assert _add(client, "Stretch", kind="restorative").status_code == 200


def test_a_bad_time_is_a_422_and_a_blank_title_a_409(client: TestClient) -> None:
    assert _add(client, "Stretch", "90").status_code == 422
    assert _add(client, "  ").status_code == 409
    assert _arts(client) == []


def test_editing_or_deleting_a_missing_art_is_a_409(client: TestClient) -> None:
    assert client.patch("/api/arts/nope", json={"title": "x"}).status_code == 409
    assert client.delete("/api/arts/nope").status_code == 409
