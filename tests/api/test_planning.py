from datetime import datetime
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _post(client: TestClient, path: str, body: dict[str, Any] | None = None) -> Any:
    return client.post(f"/api/planning/{path}", json=body)


def _planning(client: TestClient) -> dict[str, Any]:
    planning: dict[str, Any] = client.get("/api/view").json()["planning"]
    return planning


def _plan(client: TestClient, *lines: str) -> None:
    _post(client, "start")
    client.put("/api/planning/text", json={"text": "\n".join(lines)})
    assert _post(client, "proceed").status_code == 200


def test_a_new_day_starts_in_the_zero_state(client: TestClient) -> None:
    planning = _planning(client)
    assert planning["status"] == "zero" and planning["trials"] == []


def test_the_whole_flow_over_http(client: TestClient) -> None:
    assert _post(client, "start").json()["planning"]["status"] == "inscribe"
    client.put("/api/planning/text", json={"text": "Write report\nTidy desk"})
    assert _planning(client)["text"] == "Write report\nTidy desk"
    estimate = _post(client, "proceed").json()["planning"]
    assert estimate["status"] == "estimate"
    first, second = estimate["trials"]
    reply = client.patch(
        f"/api/planning/trials/{first['id']}", json={"estimate": "1h15m", "is_mandate": True}
    )
    assert reply.json()["planning"]["trials"][0]["expected_text"] == "1h15m"
    client.put("/api/planning/order", json={"ids": [second["id"], first["id"]]})
    sealed = _post(client, "seal").json()["planning"]
    assert sealed["status"] == "active"
    assert [(t["title"], t["state"]) for t in sealed["trials"]] == [
        ("Tidy desk", "immediate"),
        ("Write report", "remaining"),
    ]


def test_summon_unstage_and_abandon_keep_the_horizon_whole(client: TestClient) -> None:
    client.post(
        "/api/import",
        files={
            "file": (
                "future_trials.json",
                b'[{"id":"q_1","description":"Read","status":"Remaining",'
                b'"logical_date":"2026-10-01","expected_time_mins":30,"mandate":true}]',
            )
        },
    )
    horizon_id = _planning(client)["horizon"][0]["id"]
    _post(client, "start")
    summoned = _post(client, "summon", {"source": "horizon", "id": horizon_id}).json()["planning"]
    assert summoned["horizon"] == [] and summoned["trials"][0]["is_mandate"]
    back = _post(client, f"trials/{summoned['trials'][0]['id']}/unstage").json()["planning"]
    assert [i["id"] for i in back["horizon"]] == [horizon_id]
    _post(client, "summon", {"source": "horizon", "id": horizon_id})
    abandoned = _post(client, "abandon").json()["planning"]
    assert abandoned["status"] == "zero"
    assert [i["id"] for i in abandoned["horizon"]] == [horizon_id]


def test_sealing_with_nothing_open_is_a_409_with_a_plain_message(client: TestClient) -> None:
    _plan(client, "Only one")
    only = _planning(client)["trials"][0]["id"]
    _post(client, f"trials/{only}/dismiss")
    reply = _post(client, "seal")
    assert reply.status_code == 409 and "at least one" in reply.json()["detail"]


def test_proceeding_with_nothing_written_is_a_409(client: TestClient) -> None:
    _post(client, "start")
    assert _post(client, "proceed").status_code == 409


def test_a_bad_estimate_is_a_422(client: TestClient) -> None:
    _plan(client, "Walk")
    trial = _planning(client)["trials"][0]["id"]
    reply = client.patch(f"/api/planning/trials/{trial}", json={"estimate": "soon"})
    assert reply.status_code == 422 and "45m" in reply.json()["detail"]


def test_a_failed_step_changes_nothing(client: TestClient) -> None:
    _plan(client, "Walk")
    trial = _planning(client)["trials"][0]["id"]
    client.patch(f"/api/planning/trials/{trial}", json={"is_mandate": True, "estimate": "soon"})
    assert _planning(client)["trials"][0]["is_mandate"] is False


def test_unknown_trials_and_bad_orders_are_409s(client: TestClient) -> None:
    _plan(client, "Walk")
    assert _post(client, "trials/nope/dismiss").status_code == 409
    assert client.put("/api/planning/order", json={"ids": ["nope"]}).status_code == 409
    assert _post(client, "summon", {"source": "art", "id": "nope"}).status_code == 409


def test_the_view_after_four_next_morning_drops_an_unsealed_scroll(
    client: TestClient, clock: FixedClock
) -> None:
    _plan(client, "Walk")
    clock.set(datetime.fromisoformat("2026-10-19T04:00:00+02:00"))
    planning = _planning(client)
    assert planning["status"] == "zero" and planning["trials"] == []
