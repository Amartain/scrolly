"""Bringing back a trial postponed or let go today (owner, 2026-10-23: a double-click)."""

from typing import Any

from fastapi.testclient import TestClient


def _seal(client: TestClient, *titles: str) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")


def _view(client: TestClient) -> dict[str, Any]:
    view: dict[str, Any] = client.get("/api/view").json()
    return view


def _id(client: TestClient, title: str) -> str:
    trials = _view(client)["planning"]["trials"]
    return str(next(t["id"] for t in trials if t["title"] == title))


def test_a_postponed_trial_comes_back_on_top_and_leaves_the_horizon(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    trial = _id(client, "Tidy desk")
    client.post(f"/api/trials/{trial}/postpone")
    assert [h["title"] for h in _view(client)["planning"]["horizon"]] == ["Tidy desk"]
    view = client.post(f"/api/trials/{trial}/resummon").json()
    assert view["dashboard"]["postponed"] == []
    back = next(t for t in view["planning"]["trials"] if t["title"] == "Tidy desk")
    assert back["state"] == "remaining"
    assert view["planning"]["horizon"] == []


def test_a_fallen_leaf_comes_back_as_the_immediate_trial_when_nothing_is_at_hand(
    client: TestClient,
) -> None:
    _seal(client, "Write report")
    trial = _id(client, "Write report")
    client.post(f"/api/trials/{trial}/abandon")
    dashboard = client.post(f"/api/trials/{trial}/resummon").json()["dashboard"]
    assert dashboard["lost"] == []
    assert dashboard["immediate"]["title"] == "Write report"


def test_a_trial_still_on_the_scroll_cannot_be_summoned_back(client: TestClient) -> None:
    _seal(client, "Write report")
    assert client.post(f"/api/trials/{_id(client, 'Write report')}/resummon").status_code == 409
