from typing import Any

from fastapi.testclient import TestClient


def _view(client: TestClient) -> dict[str, Any]:
    view: dict[str, Any] = client.get("/api/view").json()
    return view


def _to_weigh(client: TestClient) -> list[dict[str, Any]]:
    client.put("/api/golden-core", json={"enabled": True})
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write report\nTidy desk"})
    client.post("/api/planning/proceed")
    reply = client.post("/api/planning/proceed").json()
    assert reply["planning"]["status"] == "weigh"
    trials: list[dict[str, Any]] = reply["planning"]["trials"]
    return trials


def test_the_view_carries_the_day_summary_and_an_uninvited_golden_core(client: TestClient) -> None:
    planning = _view(client)["planning"]
    assert planning["budget"]["light_text"] == "7h48m"
    assert planning["budget"]["trial_count"] == 0
    assert (planning["qi"]["enabled"], planning["qi"]["invited"]) == (False, False)


def test_the_day_summary_follows_the_estimates(client: TestClient) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "A\nB"})
    first, _ = client.post("/api/planning/proceed").json()["planning"]["trials"]
    client.patch(f"/api/planning/trials/{first['id']}", json={"estimate": "2h", "is_mandate": True})
    budget = _view(client)["planning"]["budget"]
    assert (budget["trial_count"], budget["planned_text"]) == (2, "2h")
    assert (budget["unestimated_count"], budget["mandate_pct"]) == (1, 26)  # 120 of 468 minutes


def test_awakening_the_golden_core_over_http(client: TestClient) -> None:
    reply = client.put("/api/golden-core", json={"enabled": True}).json()
    assert (reply["planning"]["qi"]["enabled"], reply["planning"]["qi"]["invited"]) == (True, True)


def test_weighing_and_sealing_over_http(client: TestClient) -> None:
    first, second = _to_weigh(client)
    client.patch(f"/api/planning/trials/{first['id']}", json={"qi": "60"})
    reply = client.patch(f"/api/planning/trials/{second['id']}", json={"qi": "50"}).json()
    qi = reply["planning"]["qi"]
    assert (qi["planned"], qi["start"], qi["tomorrow_start"]) == (110, 100, 90)
    assert reply["planning"]["trials"][0]["qi_text"] == "60"
    client.put("/api/planning/qi-start", json={"value": 60})
    sealed = client.post("/api/planning/seal").json()["planning"]
    assert (sealed["status"], sealed["qi"]["start"]) == ("active", 60)


def test_a_bad_qi_or_start_is_a_422(client: TestClient) -> None:
    first, _ = _to_weigh(client)
    assert (
        client.patch(f"/api/planning/trials/{first['id']}", json={"qi": "lots"}).status_code == 422
    )
    assert client.put("/api/planning/qi-start", json={"value": 500}).status_code == 422


def test_sealing_before_weighing_is_a_409(client: TestClient) -> None:
    client.put("/api/golden-core", json={"enabled": True})
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "A"})
    client.post("/api/planning/proceed")
    assert client.post("/api/planning/seal").status_code == 409
