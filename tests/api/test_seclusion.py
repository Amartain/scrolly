from datetime import timedelta
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _seal(client: TestClient, *titles: str) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")


def _state(client: TestClient) -> dict[str, Any]:
    state: dict[str, Any] = client.get("/api/seclusion").json()
    return state


def _id(client: TestClient) -> str:
    return str(_state(client)["trial"]["id"])


def test_before_anything_is_sealed_there_is_nothing_to_focus_on(client: TestClient) -> None:
    assert _state(client)["trial"] is None
    assert client.post("/api/seclusion/enter").status_code == 409


def test_entering_shows_the_immediate_trial_and_the_others_waiting(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    state = client.post("/api/seclusion/enter").json()
    assert state["active"] is True
    assert state["trial"]["title"] == "Write report"
    assert [t["title"] for t in state["remaining"]] == ["Tidy desk"]


def test_incense_counts_down_to_the_estimate_then_up_in_words_of_state(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report")
    client.patch(f"/api/trials/{_id(client)}", json={"estimate": "45m"})
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    clock.set(clock.now() + timedelta(minutes=27))
    state = _state(client)
    assert state["incense"] == {"state": "remaining", "remaining_s": 18 * 60, "over_s": 0}
    assert state["gong_in_s"] == 18 * 60
    clock.set(clock.now() + timedelta(minutes=19))
    state = _state(client)
    assert state["incense"] == {"state": "overfilled", "remaining_s": 0, "over_s": 60}
    assert state["gong_in_s"] == 30 * 60 - 60


def test_a_trial_without_an_estimate_has_no_incense_yet(client: TestClient) -> None:
    _seal(client, "Write report")
    state = client.post("/api/seclusion/enter").json()
    assert (state["incense"], state["gong_in_s"]) == (None, None)


def test_stepping_out_pauses_the_trial(client: TestClient, clock: FixedClock) -> None:
    _seal(client, "Write report")
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    clock.set(clock.now() + timedelta(minutes=5))
    state = client.post("/api/seclusion/leave").json()
    assert state["active"] is False
    assert state["trial"]["timer"]["running"] is False
    assert state["trial"]["timer"]["elapsed_s"] == 300


def test_entering_with_the_dashboard_timer_running_keeps_it_running(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report")
    client.post(f"/api/trials/{_id(client)}/timer/start")
    clock.set(clock.now() + timedelta(minutes=5))
    state = client.post("/api/seclusion/enter").json()
    assert state["trial"]["timer"] == {"elapsed_s": 300, "running": True, "expected_s": None}


def test_zero_out_clears_the_ring_but_keeps_the_logged_time(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report")
    client.patch(f"/api/trials/{_id(client)}", json={"estimate": "45m"})
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    clock.set(clock.now() + timedelta(minutes=10))
    state = client.post("/api/seclusion/timer/zero").json()
    assert state["trial"]["timer"] == {"elapsed_s": 600, "running": False, "expected_s": 2700}
    assert (state["ring_elapsed_s"], state["incense"]["remaining_s"]) == (0, 2700)


def test_a_new_timer_starts_over_at_once_and_keeps_the_logged_time(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report")
    client.patch(f"/api/trials/{_id(client)}", json={"estimate": "45m"})
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    clock.set(clock.now() + timedelta(minutes=10))
    client.post("/api/seclusion/timer/new")
    clock.set(clock.now() + timedelta(minutes=3))
    state = _state(client)
    assert state["trial"]["timer"]["elapsed_s"] == 13 * 60
    assert state["trial"]["timer"]["running"] is True
    assert state["ring_elapsed_s"] == 3 * 60


def test_conquering_in_seclusion_promotes_the_next_trial_idle(client: TestClient) -> None:
    _seal(client, "Write report", "Tidy desk")
    client.post("/api/seclusion/enter")
    client.post(f"/api/trials/{_id(client)}/conquer")
    state = _state(client)
    assert state["trial"]["title"] == "Tidy desk"
    assert state["trial"]["timer"]["running"] is False


def test_a_running_trial_carries_on_past_four_and_stepping_out_lets_the_scroll_go(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Write report", "Tidy desk")
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    clock.set(clock.now().replace(day=19, hour=4, minute=30))
    state = _state(client)
    assert state["active"] is True
    assert state["trial"]["title"] == "Write report"
    assert state["trial"]["timer"]["running"] is True
    assert client.post(f"/api/trials/{_id(client)}/conquer").status_code == 200
    assert _state(client)["trial"]["title"] == "Tidy desk"
    client.post("/api/seclusion/leave")
    dashboard = client.get("/api/view").json()["dashboard"]
    assert dashboard["immediate"] is None
