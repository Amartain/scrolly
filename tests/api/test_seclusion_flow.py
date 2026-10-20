from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from tests.api.seclusion_helpers import enter_on, later, logged, room

DIAL = {"focus_min": 2, "break_min": 1, "cycles": 2}


def test_switching_tabs_keeps_every_logged_second_and_starts_a_fresh_run(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "incense", "Write report")
    client.post("/api/seclusion/timer/start")
    later(clock, 4)
    to_cycles = client.post("/api/seclusion/discipline", json={"discipline": "cycles"}).json()
    assert to_cycles["cycles"]["phase"] == "idle"
    assert (to_cycles["trial"]["timer"]["running"], logged(client)) == (False, 240)
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 1)
    to_flow = client.post("/api/seclusion/discipline", json={"discipline": "flow"}).json()
    assert to_flow["flow"]["phase"] == "idle" and to_flow["flow"]["focus_s"] == 0
    assert logged(client) == 300
    client.post("/api/seclusion/timer/start")
    later(clock, 2)
    client.post("/api/seclusion/discipline", json={"discipline": "incense"})
    assert logged(client) == 420


def test_flow_banks_rest_at_the_ratio_and_a_break_counts_the_bank_down(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "flow", "Write report")
    client.put("/api/seclusion/flow/ratio", json={"work": 3, "rest": 2})
    client.post("/api/seclusion/timer/start")
    later(clock, 30)
    flow = room(client)["flow"]
    assert (flow["work"], flow["rest"], flow["banked_s"]) == (3, 2, 20 * 60)
    on_break = client.post("/api/seclusion/break/start").json()
    assert on_break["flow"]["break_total_s"] == 20 * 60
    assert on_break["trial"]["timer"]["running"] is False
    later(clock, 5)
    assert room(client)["flow"]["break_left_s"] == 15 * 60
    later(clock, 20)
    after = room(client)["flow"]
    assert (after["phase"], after["banked_s"]) == ("focus", 0)
    assert room(client)["trial"]["timer"]["running"] is False  # focus waits for Start


def test_ending_a_flow_break_early_keeps_the_rest_that_is_left(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "flow", "Write report")
    client.put("/api/seclusion/flow/ratio", json={"work": 1, "rest": 1})
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    client.post("/api/seclusion/break/start")
    later(clock, 4)
    state = client.post("/api/seclusion/break/end").json()
    assert state["flow"]["banked_s"] == 6 * 60


def test_conquering_stops_the_bank_from_growing(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "flow", "Write report", "Tidy desk")
    client.put("/api/seclusion/flow/ratio", json={"work": 1, "rest": 1})
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    trial_id = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": trial_id})
    later(clock, 30)
    assert room(client)["flow"]["banked_s"] == 10 * 60
    client.post("/api/seclusion/timer/start")
    later(clock, 5)
    assert room(client)["flow"]["banked_s"] == 15 * 60  # the same bank carries on


def test_the_ratio_is_fixed_while_a_bank_is_open_and_limited_to_one_to_ten(
    client: TestClient,
) -> None:
    enter_on(client, "flow", "Write report")
    assert client.put("/api/seclusion/flow/ratio", json={"work": 11, "rest": 1}).status_code == 422
    assert client.put("/api/seclusion/flow/ratio", json={"work": 1, "rest": 10}).status_code == 200
    client.post("/api/seclusion/timer/start")
    assert client.put("/api/seclusion/flow/ratio", json={"work": 2, "rest": 2}).status_code == 422


def test_a_break_needs_a_minute_banked(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "flow", "Write report")
    client.post("/api/seclusion/timer/start")
    later(clock, 2)
    assert client.post("/api/seclusion/break/start").status_code == 422


def test_sound_defaults_are_sixty_percent_and_not_muted_and_are_remembered(
    client: TestClient,
) -> None:
    assert client.get("/api/view").json()["sound"] == {"volume": 60, "muted": False}
    client.put("/api/sound", json={"volume": 20})
    client.put("/api/sound", json={"muted": True})
    assert client.get("/api/view").json()["sound"] == {"volume": 20, "muted": True}
    assert client.put("/api/sound", json={"volume": 101}).status_code == 422
