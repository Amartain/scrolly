from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from tests.api.seclusion_helpers import enter_on, later, logged, room

DIAL = {"focus_min": 2, "break_min": 1, "cycles": 2}


def test_the_dial_starts_a_focus_and_remembers_what_was_set(client: TestClient) -> None:
    enter_on(client, "cycles", "Write report")
    assert room(client)["plan"] == {"focus_min": 45, "break_min": 15, "cycles": 3}
    started = client.post("/api/seclusion/timer/start", json=DIAL).json()
    assert started["cycles"]["phase"] == "focus"
    assert started["cycles"]["remaining_s"] == 120
    assert started["trial"]["timer"]["running"] is True
    assert started["plan"] == DIAL


def test_the_room_sends_the_limits_of_its_dials(client: TestClient) -> None:
    enter_on(client, "cycles", "Write report")
    assert room(client)["limits"] == {
        "focus_max_min": 120,
        "break_max_min": 60,
        "cycles_max": 12,
        "ratio_max": 10,
    }


def test_focus_ends_at_the_set_time_even_when_nobody_looked(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 3 * 60)
    client.post(
        "/api/ghost/keep"
    )  # three hours away with a timer running: the user says they count
    state = room(client)
    # Both focuses counted, not the three hours: the trial stopped at the end of each focus.
    assert logged(client) == 240
    assert state["trial"]["timer"]["running"] is False
    assert state["cycles"]["phase"] == "done"


def test_a_break_begins_by_itself_and_so_does_the_next_focus(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 2.5)
    state = room(client)
    assert (state["cycles"]["phase"], state["cycles"]["remaining_s"]) == ("break", 30)
    assert state["trial"]["timer"]["running"] is False
    later(clock, 1)
    state = room(client)
    assert (state["cycles"]["phase"], state["cycles"]["cycle"]) == ("focus", 2)
    assert state["cycles"]["remaining_s"] == 90  # it began when the break ended, 30 s ago
    assert state["trial"]["timer"]["running"] is True
    assert logged(client) == 150


def test_two_one_minute_cycles_run_focus_break_focus_break_with_no_start_between(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json={"focus_min": 1, "break_min": 1, "cycles": 2})
    seen = []
    for _ in range(5):
        later(clock, 0.5)
        seen.append(room(client)["cycles"]["phase"])
        later(clock, 0.5)
    assert seen == ["focus", "break", "focus", "break", "done"]
    assert logged(client) == 120


def test_a_trial_waiting_after_a_conquest_joins_the_next_focus_by_itself(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report", "Tidy desk")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 2.5)  # on the break
    first = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": first})
    later(clock, 1)  # the second focus began 30 s ago
    state = room(client)
    assert state["trial"]["title"] == "Tidy desk"
    assert (state["trial"]["timer"]["running"], logged(client)) == (True, 30)


def test_the_last_cycle_ends_done_and_nothing_counts_on(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json={"focus_min": 1, "break_min": 1, "cycles": 1})
    later(clock, 10)
    assert room(client)["cycles"]["phase"] == "done"
    assert logged(client) == 60


def test_conquering_mid_focus_does_not_stop_the_cycle_and_the_next_trial_joins_it(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report", "Tidy desk")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 0.5)
    trial_id = room(client)["trial"]["id"]
    after = client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": trial_id})
    assert after.json()["trial"]["title"] == "Tidy desk"
    later(clock, 0.5)
    assert room(client)["cycles"]["remaining_s"] == 60  # the cycle's own clock kept going
    carried = client.post("/api/seclusion/timer/start").json()
    assert carried["cycles"]["cycle"] == 1 and carried["cycles"]["phase"] == "focus"
    assert carried["trial"]["timer"]["running"] is True
    later(clock, 1)
    assert room(client)["cycles"]["phase"] == "break"
    assert logged(client) == 60  # Tidy desk only logs the time it was worked on


def test_unchosen_after_a_conquest_the_break_still_comes_on_schedule(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report", "Tidy desk")
    client.post("/api/seclusion/timer/start", json=DIAL)
    trial_id = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": trial_id})
    later(clock, 2.5)
    assert room(client)["cycles"]["phase"] == "break"


def test_taking_a_break_now_stops_the_trial_and_skipping_it_starts_the_next_focus(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 1)
    state = client.post("/api/seclusion/break/start").json()
    assert (state["cycles"]["phase"], state["cycles"]["remaining_s"]) == ("break", 60)
    assert state["trial"]["timer"]["running"] is False
    assert logged(client) == 60
    skipped = client.post("/api/seclusion/break/end").json()
    assert (skipped["cycles"]["phase"], skipped["cycles"]["cycle"]) == ("focus", 2)
    assert skipped["trial"]["timer"]["running"] is True


def test_three_cycles_run_one_after_the_other_through_the_break_buttons(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    state = client.post(
        "/api/seclusion/timer/start", json={"focus_min": 2, "break_min": 1, "cycles": 3}
    ).json()
    seen = []
    for _ in range(2):
        seen.append((state["cycles"]["cycle"], state["cycles"]["cycles"], state["cycles"]["phase"]))
        later(clock, 1)
        client.post("/api/seclusion/break/start")
        state = client.post("/api/seclusion/break/end").json()
    seen.append((state["cycles"]["cycle"], state["cycles"]["cycles"], state["cycles"]["phase"]))
    assert seen == [(1, 3, "focus"), (2, 3, "focus"), (3, 3, "focus")]
    later(clock, 4)  # the third focus and its break run their course
    assert room(client)["cycles"]["phase"] == "done"


def test_settings_outside_their_limits_are_refused(client: TestClient) -> None:
    enter_on(client, "cycles", "Write report")
    for bad in (
        {"focus_min": 121, "break_min": 15, "cycles": 3},
        {"focus_min": 45, "break_min": 0, "cycles": 3},
        {"focus_min": 45, "break_min": 15, "cycles": 13},
    ):
        assert client.post("/api/seclusion/timer/start", json=bad).status_code == 422
    assert room(client)["cycles"]["phase"] == "idle"


def test_stepping_out_pauses_the_cycle_and_the_trial(client: TestClient, clock: FixedClock) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json=DIAL)
    later(clock, 1)
    client.post("/api/seclusion/leave")
    later(clock, 30)
    client.post("/api/seclusion/enter")
    state = room(client)
    assert (state["cycles"]["phase"], state["cycles"]["remaining_s"]) == ("focus", 60)
    assert state["cycles"]["running"] is False
