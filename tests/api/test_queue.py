import json
from typing import Any

from fastapi.testclient import TestClient


def _view(client: TestClient) -> dict[str, Any]:
    body: dict[str, Any] = client.get("/api/view").json()
    return body


def _seal(client: TestClient, *titles: str) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")


def _titles(client: TestClient, state: str) -> list[str]:
    trials = _view(client)["planning"]["trials"]
    return [t["title"] for t in trials if t["state"] == state]


def _id(client: TestClient, title: str) -> str:
    return str(next(t["id"] for t in _view(client)["planning"]["trials"] if t["title"] == title))


def _import(client: TestClient, name: str, items: list[dict[str, Any]]) -> None:
    client.post("/api/import", files={"file": (name, json.dumps(items).encode())})


def test_scribing_after_the_seal_queues_a_trial_with_estimate_and_qi(client: TestClient) -> None:
    _seal(client, "A")
    reply = client.post("/api/trials", json={"title": "Pay rent", "estimate": "20m", "qi": "10"})
    scribed = next(t for t in reply.json()["planning"]["trials"] if t["title"] == "Pay rent")
    assert (scribed["state"], scribed["expected_text"], scribed["qi_text"]) == (
        "remaining",
        "20m",
        "10",
    )


def test_a_scribed_trial_lands_first_in_the_queue(client: TestClient) -> None:
    _seal(client, "A", "B", "C")
    client.post("/api/trials", json={"title": "Pay rent"})
    trials = client.get("/api/view").json()["planning"]["trials"]
    waiting = [t["title"] for t in trials if t["state"] == "remaining"]
    assert waiting == ["Pay rent", "B", "C"]


def test_scribing_needs_a_title(client: TestClient) -> None:
    _seal(client, "A")
    assert client.post("/api/trials", json={"title": " "}).status_code == 409


def test_promoting_swaps_it_with_the_immediate_trial(client: TestClient) -> None:
    _seal(client, "A", "B", "C")
    client.post(f"/api/trials/{_id(client, 'C')}/promote")
    assert _titles(client, "immediate") == ["C"]
    assert _titles(client, "remaining") == ["A", "B"]


def test_only_a_remaining_trial_can_be_promoted(client: TestClient) -> None:
    _seal(client, "A", "B")
    assert client.post(f"/api/trials/{_id(client, 'A')}/promote").status_code == 409


def test_remaining_trials_can_be_reordered_and_a_bad_order_is_refused(client: TestClient) -> None:
    _seal(client, "A", "B", "C", "D")
    ids = [_id(client, t) for t in ("D", "B", "C")]
    assert client.put("/api/trials/order", json={"ids": ids}).status_code == 200
    assert _titles(client, "remaining") == ["D", "B", "C"]
    assert client.put("/api/trials/order", json={"ids": ids[:2]}).status_code == 409


def test_a_remaining_trial_can_be_postponed_or_abandoned(client: TestClient) -> None:
    _seal(client, "A", "B", "C")
    client.post(f"/api/trials/{_id(client, 'B')}/postpone")
    client.post(f"/api/trials/{_id(client, 'C')}/abandon")
    dashboard = _view(client)["dashboard"]
    assert [t["title"] for t in dashboard["postponed"]] == ["B"]
    assert [t["title"] for t in dashboard["lost"]] == ["C"]
    assert [i["title"] for i in _view(client)["planning"]["horizon"]] == ["B"]


def test_summoning_after_the_seal_moves_a_horizon_item_to_the_queue(client: TestClient) -> None:
    _import(
        client,
        "future_trials.json",
        [
            {
                "id": "q_1",
                "description": "Read",
                "status": "Remaining",
                "logical_date": "2026-10-01",
                "expected_time_mins": 30,
                "mandate": True,
            }
        ],
    )
    _import(
        client, "rituals.json", [{"id": "r_a1", "description": "Stretch", "expected_time_mins": 15}]
    )
    _seal(client, "A")
    view = _view(client)
    horizon_id, art_id = (
        view["planning"]["horizon"][0]["id"],
        view["planning"]["foundational"][0]["id"],
    )
    client.post("/api/trials/summon", json={"source": "horizon", "id": horizon_id})
    client.post("/api/trials/summon", json={"source": "art", "id": art_id})
    view = _view(client)
    assert view["planning"]["horizon"] == []
    assert _titles(client, "remaining") == ["Read", "Stretch"]
    assert len(view["planning"]["foundational"]) == 1


def test_summoning_something_missing_is_refused(client: TestClient) -> None:
    _seal(client, "A")
    assert (
        client.post("/api/trials/summon", json={"source": "horizon", "id": "nope"}).status_code
        == 409
    )


def test_the_horizon_can_be_added_to_edited_discarded_and_reordered(client: TestClient) -> None:
    client.post("/api/horizon", json={"title": "First"})
    client.post("/api/horizon", json={"title": "Second"})
    items = _view(client)["planning"]["horizon"]
    assert [i["title"] for i in items] == ["Second", "First"]
    second, first = items[0]["id"], items[1]["id"]
    client.patch(f"/api/horizon/{first}", json={"title": "First!", "estimate": "1h"})
    client.put("/api/horizon/order", json={"ids": [first, second]})
    items = _view(client)["planning"]["horizon"]
    assert [(i["title"], i["expected_text"]) for i in items] == [("First!", "1h"), ("Second", "")]
    client.delete(f"/api/horizon/{second}")
    assert [i["title"] for i in _view(client)["planning"]["horizon"]] == ["First!"]
    assert client.delete(f"/api/horizon/{second}").status_code == 409
    assert client.post("/api/horizon", json={"title": " "}).status_code == 409


def test_a_horizon_idea_can_be_added_with_an_estimate(client: TestClient) -> None:
    client.post("/api/horizon", json={"title": "Garden", "estimate": "45m"})
    bad = client.post("/api/horizon", json={"title": "Weed", "estimate": "90"})
    assert bad.status_code == 422
    items = _view(client)["planning"]["horizon"]
    assert [(i["title"], i["expected_text"]) for i in items] == [("Garden", "45m")]


def test_arts_can_be_reordered_within_their_kind(client: TestClient) -> None:
    _import(
        client,
        "rituals.json",
        [
            {"id": "r_1", "description": "One", "expected_time_mins": 5},
            {"id": "r_2", "description": "Two", "expected_time_mins": 5},
        ],
    )
    ids = [a["id"] for a in _view(client)["planning"]["foundational"]]
    reply = client.put("/api/arts/order", json={"kind": "foundational", "ids": ids[::-1]})
    assert [a["id"] for a in reply.json()["planning"]["foundational"]] == ids[::-1]
    assert (
        client.put("/api/arts/order", json={"kind": "foundational", "ids": ids[:1]}).status_code
        == 409
    )


def test_the_estimate_of_a_waiting_trial_can_be_set_after_the_seal(client: TestClient) -> None:
    _seal(client, "A", "B")
    waiting = _id(client, "B")
    assert client.patch(f"/api/trials/{waiting}", json={"estimate": "soon"}).status_code == 422
    reply = client.patch(f"/api/trials/{waiting}", json={"estimate": "1h15m"})
    assert (
        next(t for t in reply.json()["planning"]["trials"] if t["id"] == waiting)["expected_text"]
        == "1h15m"
    )
    again = client.patch(f"/api/trials/{waiting}", json={"estimate": "2h"})
    assert again.status_code == 409 and "already set" in again.json()["detail"]


def test_a_horizon_item_switches_between_mandate_and_mortal(client: TestClient) -> None:
    client.post("/api/horizon", json={"title": "Read"})
    item = _view(client)["planning"]["horizon"][0]
    assert item["type"] == "mortal"
    reply = client.patch(f"/api/horizon/{item['id']}", json={"is_mandate": True})
    assert reply.json()["planning"]["horizon"][0]["type"] == "mandate"
