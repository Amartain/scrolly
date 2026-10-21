from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _seal(client: TestClient, *titles: str) -> list[dict[str, Any]]:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    reply = client.post("/api/planning/seal").json()
    trials: list[dict[str, Any]] = reply["planning"]["trials"]
    return trials


def _dashboard(client: TestClient) -> dict[str, Any]:
    dashboard: dict[str, Any] = client.get("/api/view").json()["dashboard"]
    return dashboard


def _id(client: TestClient, title: str) -> str:
    trials = client.get("/api/view").json()["planning"]["trials"]
    return str(next(t["id"] for t in trials if t["title"] == title))


def test_a_sealed_day_shows_its_immediate_trial_with_a_stopped_timer(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    immediate = _dashboard(client)["immediate"]
    assert immediate["title"] == "Write report"
    assert immediate["timer"] == {"elapsed_s": 0, "running": False, "expected_s": None}


def test_the_timer_follows_the_server_clock_not_the_requests(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report")
    client.post(f"/api/trials/{_id(client, 'Write report')}/timer/start")
    clock.set(clock.now() + timedelta(minutes=20))
    timer = _dashboard(client)["immediate"]["timer"]
    assert (timer["elapsed_s"], timer["running"]) == (1200, True)


def test_pause_and_reset(client: TestClient, clock: FixedClock) -> None:
    _seal(client, "Write report")
    trial = _id(client, "Write report")
    client.post(f"/api/trials/{trial}/timer/start")
    clock.set(clock.now() + timedelta(minutes=5))
    client.post(f"/api/trials/{trial}/timer/pause")
    clock.set(clock.now() + timedelta(hours=1))
    assert _dashboard(client)["immediate"]["timer"]["elapsed_s"] == 300
    client.post(f"/api/trials/{trial}/timer/reset")
    assert _dashboard(client)["immediate"]["timer"]["elapsed_s"] == 0


def test_conquering_lists_the_trial_and_promotes_the_next(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report", "Tidy desk")
    trial = _id(client, "Write report")
    client.post(f"/api/trials/{trial}/timer/start")
    clock.set(clock.now() + timedelta(minutes=31))
    dashboard = client.post(f"/api/trials/{trial}/conquer").json()["dashboard"]
    assert dashboard["immediate"]["title"] == "Tidy desk"
    assert [(c["title"], c["actual_text"]) for c in dashboard["conquered"]] == [
        ("Write report", "31m")
    ]
    assert dashboard["essence"]["actual_text"] == "31m"


def test_the_last_conquest_is_a_victory(client: TestClient) -> None:
    _seal(client, "Only one")
    dashboard = client.post(f"/api/trials/{_id(client, 'Only one')}/conquer").json()["dashboard"]
    assert (dashboard["victory"], dashboard["immediate"]) == (True, None)


def test_a_conquered_trial_is_read_only_until_it_is_revived(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    trial = _id(client, "Write report")
    client.post(f"/api/trials/{trial}/conquer")
    for patch in ({"title": "Other"}, {"is_mandate": True}, {"estimate": "1h"}, {"qi": "5"}):
        reply = client.patch(f"/api/trials/{trial}", json=patch)
        assert reply.status_code == 409 and "Revive" in reply.json()["detail"]
    revived = client.post(f"/api/trials/{trial}/revive").json()["dashboard"]
    assert revived["conquered"] == []
    assert client.patch(f"/api/trials/{trial}", json={"title": "Other"}).status_code == 200


def test_postponing_sends_a_copy_to_the_horizon(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    reply = client.post(f"/api/trials/{_id(client, 'Write report')}/postpone").json()
    assert [item["title"] for item in reply["planning"]["horizon"]] == ["Write report"]
    assert reply["dashboard"]["immediate"]["title"] == "Tidy desk"


def test_a_mandate_cannot_be_abandoned(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    trial = _id(client, "Write report")
    client.patch(f"/api/trials/{trial}", json={"is_mandate": True})
    reply = client.post(f"/api/trials/{trial}/abandon")
    assert reply.status_code == 409
    assert "Postpone" in reply.json()["detail"]


def test_a_mortal_can_be_abandoned(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    reply = client.post(f"/api/trials/{_id(client, 'Write report')}/abandon").json()
    assert reply["dashboard"]["immediate"]["title"] == "Tidy desk"


def test_nothing_works_before_the_day_is_sealed(client: TestClient) -> None:
    reply = client.post("/api/trials/anything/conquer")
    assert (reply.status_code, reply.json()["detail"]) == (409, "The day has not begun yet")


def test_conquered_qi_moves_the_dashboard_gauge(client: TestClient) -> None:
    client.put("/api/golden-core", json={"enabled": True})
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write report\nTidy desk"})
    client.post("/api/planning/proceed")
    client.post("/api/planning/proceed")
    trial = _id(client, "Write report")
    client.patch(f"/api/planning/trials/{trial}", json={"qi": "40"})
    client.post("/api/planning/seal")
    assert client.get("/api/view").json()["planning"]["qi"]["spent"] == 0
    qi = client.post(f"/api/trials/{trial}/conquer").json()["planning"]["qi"]
    assert qi["spent"] == 40
    assert qi["spent_fill"]["calm_pct"] > 0


def test_the_qi_a_conquest_took_can_be_told_afterwards(client: TestClient) -> None:
    client.put("/api/golden-core", json={"enabled": True})
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write report\nTidy desk"})
    client.post("/api/planning/proceed")
    client.post("/api/planning/proceed")
    trial = _id(client, "Write report")
    client.post("/api/planning/seal")
    client.post(f"/api/trials/{trial}/conquer")
    spent = client.put(f"/api/trials/{trial}/qi", json={"qi": 55}).json()["planning"]["qi"]["spent"]
    assert spent == 55
    assert client.put(f"/api/trials/{trial}/qi", json={"qi": 101}).status_code == 422
    open_trial = _id(client, "Tidy desk")
    assert client.put(f"/api/trials/{open_trial}/qi", json={"qi": 5}).status_code == 409


def test_the_counters_start_at_zero_and_grow_with_the_day(client: TestClient) -> None:
    assert _dashboard(client)["lifetime_conquered"] == 0
    assert _dashboard(client)["heavenly_cycles"] == 0
    _seal(client, "A", "B")
    assert _dashboard(client)["heavenly_cycles"] == 1
    first = _id(client, "A")
    client.post(f"/api/trials/{first}/conquer")
    assert _dashboard(client)["lifetime_conquered"] == 1
    client.post(f"/api/trials/{first}/revive")
    assert _dashboard(client)["lifetime_conquered"] == 0


def test_the_dashboard_carries_both_charts_for_each_metric(client: TestClient) -> None:
    _seal(client, "A", "B")
    charts = _dashboard(client)["charts"]
    assert [c["metric"] for c in charts] == ["trials", "essence"]
    assert all(c["placeholder"] for c in charts)
    first = _dashboard(client)["immediate"]["id"]
    client.post(f"/api/trials/{first}/conquer")
    trials = _dashboard(client)["charts"][0]
    assert trials["placeholder"] is False
    assert [(p["value"], p["value_text"]) for p in trials["momentum"]] == [(1, "1")]
    assert len(trials["rhythm"]) == 7
    assert trials["rhythm"][-1]["is_rest"] is False
