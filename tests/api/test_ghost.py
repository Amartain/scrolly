from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from scrolly.storage.store import SqliteStores
from tests.api.seclusion_helpers import enter_on, later, room, seal

TEN_MINUTES = 10 * 60


def _view(client: TestClient) -> dict[str, Any]:
    view: dict[str, Any] = client.get("/api/view").json()
    return view


def _timer(client: TestClient) -> tuple[int, bool]:
    timer = _view(client)["dashboard"]["immediate"]["timer"]
    return timer["elapsed_s"], timer["running"]


def _run_dashboard_timer_for_ten_minutes(client: TestClient, clock: FixedClock) -> None:
    seal(client, "Write report", "Tidy desk")
    trial = _view(client)["dashboard"]["immediate"]["id"]
    client.post(f"/api/trials/{trial}/timer/start")
    later(clock, 10)
    _view(client)  # the user is still here at the ten-minute mark


def _last_seen(stores: SqliteStores) -> str:
    with stores() as store:
        return str((store.settings.get("ghost") or {})["last_seen"])


def test_requests_close_together_write_last_seen_once(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    _view(client)
    first = _last_seen(stores)
    later(clock, 0.1)  # six seconds on
    _view(client)
    assert _last_seen(stores) == first
    later(clock, 1)
    _view(client)
    assert _last_seen(stores) != first


def test_a_long_silence_with_a_timer_running_pauses_it_and_asks(
    client: TestClient, clock: FixedClock
) -> None:
    _run_dashboard_timer_for_ten_minutes(client, clock)
    later(clock, 2 * 60)
    view = _view(client)
    assert view["ghost"] == {"left_text": "13:22", "gap_text": "2h"}
    assert _timer(client) == (TEN_MINUTES, False)  # paused where the user left


def test_keeping_the_time_carries_every_timer_on_as_if_it_never_stopped(
    client: TestClient, clock: FixedClock
) -> None:
    _run_dashboard_timer_for_ten_minutes(client, clock)
    later(clock, 2 * 60)
    kept = client.post("/api/ghost/keep").json()
    assert kept["ghost"] is None
    assert _timer(client) == (TEN_MINUTES + 2 * 3600, True)


def test_counting_only_until_the_user_left_keeps_the_timer_where_it_stopped(
    client: TestClient, clock: FixedClock
) -> None:
    _run_dashboard_timer_for_ten_minutes(client, clock)
    later(clock, 2 * 60)
    cut = client.post("/api/ghost/cut").json()
    assert cut["ghost"] is None
    assert _timer(client) == (TEN_MINUTES, False)
    later(clock, 5)
    assert _view(client)["ghost"] is None  # asked once, not again


def test_the_question_waits_unanswered_and_the_timer_stays_paused(
    client: TestClient, clock: FixedClock
) -> None:
    _run_dashboard_timer_for_ten_minutes(client, clock)
    later(clock, 2 * 60)
    assert _view(client)["ghost"] is not None
    later(clock, 60)
    assert _view(client)["ghost"] == {"left_text": "13:22", "gap_text": "2h"}
    assert _timer(client) == (TEN_MINUTES, False)


def test_an_hour_and_a_half_is_not_a_silence_and_nothing_running_asks_nothing(
    client: TestClient, clock: FixedClock
) -> None:
    _run_dashboard_timer_for_ten_minutes(client, clock)
    later(clock, 90)
    assert _view(client)["ghost"] is None
    assert _timer(client) == (TEN_MINUTES + 90 * 60, True)
    client.post(f"/api/trials/{_view(client)['dashboard']['immediate']['id']}/timer/pause")
    later(clock, 5 * 60)
    assert _view(client)["ghost"] is None  # nothing was running while the user was away


def test_a_planning_timer_left_running_is_asked_about_too(
    client: TestClient, clock: FixedClock
) -> None:
    client.post("/api/planning/start")
    client.post("/api/planning/timer/start")
    later(clock, 10)
    _view(client)
    later(clock, 3 * 60)
    view = _view(client)
    assert view["ghost"]["gap_text"] == "3h"
    assert view["planning"]["timer"] == {
        "elapsed_s": TEN_MINUTES,
        "running": False,
        "expected_s": None,
    }
    kept = client.post("/api/ghost/keep").json()
    assert kept["planning"]["timer"]["elapsed_s"] == TEN_MINUTES + 3 * 3600
    assert kept["planning"]["timer"]["running"] is True


def test_cycles_pause_with_the_trial_and_carry_on_when_the_time_is_kept(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    long_focus = {"focus_min": 120, "break_min": 15, "cycles": 2}
    client.post("/api/seclusion/timer/start", json=long_focus)
    later(clock, 10)
    room(client)
    later(clock, 100)  # a hundred minutes away, inside a two-hour focus
    assert _view(client)["ghost"] is not None
    paused = room(client)["cycles"]
    assert (paused["phase"], paused["remaining_s"], paused["running"]) == ("focus", 6600, False)
    client.post("/api/ghost/keep")
    resumed = room(client)["cycles"]
    assert (resumed["remaining_s"], resumed["running"]) == (600, True)


def test_cutting_a_cycles_focus_leaves_it_paused_where_the_user_left(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "cycles", "Write report")
    client.post("/api/seclusion/timer/start", json={"focus_min": 120, "break_min": 15, "cycles": 2})
    later(clock, 10)
    room(client)
    later(clock, 100)
    client.post("/api/ghost/cut")
    cycles = room(client)["cycles"]
    assert (cycles["remaining_s"], cycles["running"]) == (6600, False)
    assert room(client)["trial"]["timer"]["elapsed_s"] == TEN_MINUTES


def test_a_flow_bank_stops_earning_while_away_unless_the_time_is_kept(
    client: TestClient, clock: FixedClock
) -> None:
    enter_on(client, "flow", "Write report")
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    room(client)
    later(clock, 2 * 60)
    assert room(client)["flow"]["focus_s"] == TEN_MINUTES
    client.post("/api/ghost/keep")
    assert room(client)["flow"]["focus_s"] == TEN_MINUTES + 2 * 3600
    assert room(client)["flow"]["running"] is True
