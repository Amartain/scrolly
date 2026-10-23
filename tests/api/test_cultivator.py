"""The cultivator of the peak, through the API: the dashboard header and the room agree."""

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from tests.api.seclusion_helpers import enter_on, later, room, seal


def _up(client: TestClient) -> bool:
    return bool(client.get("/api/view").json()["on_peak"])


def _trial(client: TestClient) -> str:
    return str(room(client)["trial"]["id"])


def test_the_dashboard_timer_sends_them_up_and_a_pause_leaves_them_there(
    client: TestClient,
) -> None:
    seal(client, "Write report", "Tidy desk")
    assert _up(client) is False
    trial = _trial(client)
    client.post(f"/api/trials/{trial}/timer/start")
    assert _up(client) is True
    client.post(f"/api/trials/{trial}/timer/pause")
    assert _up(client) is True
    assert room(client)["on_peak"] is True


def test_conquering_keeps_them_meditating_until_no_trial_is_left(client: TestClient) -> None:
    seal(client, "Write report", "Tidy desk")
    client.post(f"/api/trials/{_trial(client)}/timer/start")
    client.post(f"/api/trials/{_trial(client)}/conquer")
    assert _up(client) is True
    client.post(f"/api/trials/{_trial(client)}/conquer")
    assert _up(client) is False


def test_they_come_down_when_the_cycles_session_ends(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "cycles", "Write report", "Tidy desk")
    client.post("/api/seclusion/timer/start", json={"focus_min": 1, "break_min": 1, "cycles": 2})
    later(clock, 1.5)
    assert room(client)["on_peak"] is True  # a break keeps them up
    later(clock, 3)
    assert room(client)["cycles"]["phase"] == "done"
    assert room(client)["on_peak"] is False
