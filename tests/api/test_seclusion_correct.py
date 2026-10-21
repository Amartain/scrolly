"""Restart, Zero out and Stop: the user's own corrections of the room's timer."""

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from tests.api.seclusion_helpers import enter_on, later, logged, room

DIAL = {"focus_min": 30, "break_min": 5, "cycles": 3}


def test_incense_restart_scraps_the_ring_and_lights_it_again(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "incense", "Write report")
    trial_id = room(client)["trial"]["id"]
    client.patch(f"/api/trials/{trial_id}", json={"estimate": "45m"})
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    assert room(client)["restart_scrap_s"] == 600
    state = client.post("/api/seclusion/timer/new").json()
    assert state["trial"]["timer"] == {"elapsed_s": 0, "running": True, "expected_s": 2700}
    assert (state["ring_elapsed_s"], state["incense"]["remaining_s"]) == (0, 2700)
    later(clock, 3)
    assert (logged(client), room(client)["ring_elapsed_s"]) == (180, 180)


def test_incense_has_no_zero_out_and_no_stop(client: TestClient) -> None:
    enter_on(client, "incense", "Write report")
    assert client.post("/api/seclusion/timer/zero").status_code == 422
    assert client.post("/api/seclusion/timer/stop").status_code == 422


def test_cycles_zero_out_starts_the_cycle_under_way_over_and_scraps_its_minutes(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 10)
    client.post("/api/seclusion/break/start")
    client.post("/api/seclusion/break/end")
    client.post("/api/seclusion/timer/start")  # cycle 2
    later(clock, 27)
    assert (room(client)["zero_scrap_s"], room(client)["restart_scrap_s"]) == (27 * 60, 37 * 60)
    state = client.post("/api/seclusion/timer/zero").json()
    assert (state["cycles"]["cycle"], state["cycles"]["phase"]) == (2, "focus")
    assert (state["cycles"]["remaining_s"], state["cycles"]["running"]) == (30 * 60, True)
    assert (logged(client), state["trial"]["timer"]["running"]) == (600, True)


def test_cycles_zero_out_while_paused_stays_paused(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 5)
    client.post("/api/seclusion/timer/pause")
    state = client.post("/api/seclusion/timer/zero").json()
    assert (state["cycles"]["running"], state["trial"]["timer"]["running"]) == (False, False)
    assert logged(client) == 0


def test_cycles_restart_scraps_the_whole_run_and_begins_at_cycle_one(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 10)
    client.post("/api/seclusion/break/start")
    client.post("/api/seclusion/break/end")
    client.post("/api/seclusion/timer/start")
    later(clock, 4)
    assert room(client)["restart_scrap_s"] == 14 * 60
    state = client.post("/api/seclusion/timer/new").json()
    assert (state["cycles"]["cycle"], state["cycles"]["phase"]) == (1, "focus")
    assert (logged(client), state["trial"]["timer"]["running"]) == (0, True)


def test_stop_returns_the_dial_and_keeps_the_time(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 7)
    state = client.post("/api/seclusion/timer/stop").json()
    assert state["cycles"]["phase"] == "idle"
    assert (logged(client), state["trial"]["timer"]["running"]) == (420, False)


def test_flow_zero_out_drops_the_stretch_since_the_last_break(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "flow", "Write report")
    client.put("/api/seclusion/flow/ratio", json={"work": 1, "rest": 1})
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    client.post("/api/seclusion/break/start")
    later(clock, 2)
    client.post("/api/seclusion/break/end")
    client.post("/api/seclusion/timer/start")
    later(clock, 6)
    state = client.post("/api/seclusion/timer/zero").json()
    assert (state["flow"]["focus_s"], state["flow"]["banked_s"]) == (600, 480)
    assert logged(client) == 600


def test_the_next_trial_in_a_cycle_scraps_only_its_own_time(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report", "Tidy desk")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 5)
    first = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": first})
    client.post("/api/seclusion/timer/start")  # Tidy desk joins cycle 1
    later(clock, 3)
    assert room(client)["zero_scrap_s"] == 180
    client.post("/api/seclusion/timer/zero")
    assert logged(client) == 0
    done = client.get("/api/view").json()["dashboard"]["conquered"]
    assert [c["actual_text"] for c in done] == ["5m"]  # the conquered one is untouched
