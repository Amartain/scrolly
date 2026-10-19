from typing import Any

from fastapi.testclient import TestClient


def _seal(client: TestClient, *titles: str) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")


def _view(client: TestClient) -> dict[str, Any]:
    body: dict[str, Any] = client.get("/api/view").json()
    return body


def _id(client: TestClient, title: str) -> str:
    return str(next(t["id"] for t in _view(client)["planning"]["trials"] if t["title"] == title))


def test_the_estimated_qi_of_the_immediate_trial_can_be_edited(client: TestClient) -> None:
    _seal(client, "Write report")
    trial_id = _id(client, "Write report")
    reply = client.patch(f"/api/trials/{trial_id}", json={"qi": "35"})
    assert reply.json()["dashboard"]["immediate"]["qi_text"] == "35"


def test_the_actual_qi_defaults_to_the_estimate_and_can_be_corrected(client: TestClient) -> None:
    _seal(client, "Write report")
    trial_id = _id(client, "Write report")
    client.patch(f"/api/trials/{trial_id}", json={"qi": "35"})
    done = client.post(f"/api/trials/{trial_id}/conquer").json()
    assert done["dashboard"]["conquered"][0]["qi_text"] == "35"
    assert done["planning"]["qi"]["spent"] == 35
    corrected = client.patch(f"/api/trials/{trial_id}", json={"actual_qi": "60"}).json()
    assert corrected["dashboard"]["conquered"][0]["qi_text"] == "60"
    assert corrected["planning"]["qi"]["spent"] == 60


def test_a_bad_qi_is_explained(client: TestClient) -> None:
    _seal(client, "Write report")
    reply = client.patch(f"/api/trials/{_id(client, 'Write report')}", json={"qi": "lots"})
    assert reply.status_code == 422
    assert "whole number" in reply.json()["detail"]
