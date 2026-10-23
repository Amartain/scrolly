"""The way up to Seclusion through the API: the interval, the welcome, and where a focus began."""

from typing import Any

from fastapi.testclient import TestClient

from tests.api.seclusion_helpers import enter_on, room, seal


def _travel(client: TestClient) -> dict[str, Any]:
    travel: dict[str, Any] = client.get("/api/view").json()["travel"]
    return travel


def test_the_full_animation_shows_again_after_15_minutes_until_changed(client: TestClient) -> None:
    assert _travel(client) == {"interval_min": 15, "welcomed": False, "room_focus": False}
    assert client.put("/api/travel", json={"interval_min": 0}).status_code == 200
    assert _travel(client)["interval_min"] == 0


def test_an_interval_past_two_hours_is_refused(client: TestClient) -> None:
    assert client.put("/api/travel", json={"interval_min": 121}).status_code != 200
    assert _travel(client)["interval_min"] == 15


def test_the_welcome_is_remembered_and_leaves_the_interval_alone(client: TestClient) -> None:
    client.put("/api/travel", json={"interval_min": 5})
    client.put("/api/travel", json={"welcomed": True})
    assert _travel(client) == {"interval_min": 5, "welcomed": True, "room_focus": False}


def test_a_dashboard_timer_counts_as_the_rooms_once_the_room_takes_it_over(
    client: TestClient,
) -> None:
    seal(client, "Write report")
    client.post(f"/api/trials/{room(client)['trial']['id']}/timer/start")
    assert _travel(client)["room_focus"] is False
    client.post("/api/seclusion/enter")
    assert _travel(client)["room_focus"] is True


def test_a_cycles_run_in_its_break_is_the_rooms(client: TestClient) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json={"focus_min": 1, "break_min": 1, "cycles": 2})
    client.post("/api/seclusion/break/start")
    client.post("/api/seclusion/leave")
    assert _travel(client)["room_focus"] is True
