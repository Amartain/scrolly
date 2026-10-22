from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from scrolly.domain.segments import Discipline
from scrolly.storage.store import SqliteStores
from tests.api.seclusion_helpers import later, room, seal

PARALLEL = "/api/seclusion/parallel"


def _enter(client: TestClient, *titles: str) -> None:
    seal(client, *titles)
    client.post("/api/seclusion/enter")


def _waiting(client: TestClient, title: str) -> str:
    return str(next(t["id"] for t in room(client)["remaining"] if t["title"] == title))


def _pick_new(client: TestClient, title: str) -> dict[str, Any]:
    state: dict[str, Any] = client.post(PARALLEL, json={"source": "new", "ref": title}).json()
    return state


def _elapsed(trial: dict[str, Any]) -> int:
    return int(trial["timer"]["elapsed_s"])


def test_the_search_finds_waiting_trials_but_not_the_one_at_hand(client: TestClient) -> None:
    _enter(client, "Write report", "Tend the tea", "Sweep the pavilion")
    found = client.get(f"{PARALLEL}/search", params={"q": "e"}).json()
    assert [(c["source"], c["title"]) for c in found] == [
        ("remaining", "Tend the tea"),
        ("remaining", "Sweep the pavilion"),
    ]


def test_a_new_title_runs_beside_the_main_trial_with_a_timer_of_its_own(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report")
    picked = _pick_new(client, "Tend the tea")
    assert picked["parallel"]["title"] == "Tend the tea"
    assert picked["parallel"]["timer"]["running"] is False  # nothing starts on its own
    client.post("/api/seclusion/timer/start")
    later(clock, 5)
    client.post(f"{PARALLEL}/start")
    later(clock, 10)
    state = room(client)
    assert _elapsed(state["trial"]) == 15 * 60
    assert _elapsed(state["parallel"]) == 10 * 60  # never added to the main trial
    paused = client.post(f"{PARALLEL}/pause").json()
    assert paused["parallel"]["timer"]["running"] is False
    assert paused["trial"]["timer"]["running"] is True


def test_a_waiting_trial_can_be_picked_and_only_one_runs_beside(client: TestClient) -> None:
    _enter(client, "Write report", "Tend the tea", "Sweep the pavilion")
    tea = _waiting(client, "Tend the tea")
    assert client.post(PARALLEL, json={"source": "remaining", "ref": tea}).status_code == 200
    second = client.post(PARALLEL, json={"source": "new", "ref": "Water the plants"})
    assert second.status_code == 409
    assert "Only one" in second.json()["detail"]


def test_the_trial_run_beside_is_not_offered_to_switch_to(client: TestClient) -> None:
    _enter(client, "Write report", "Tend the tea")
    _pick_new(client, "Sweep the pavilion")
    assert [t["title"] for t in room(client)["remaining"]] == ["Tend the tea"]


def test_the_trial_at_hand_cannot_run_beside_itself(client: TestClient) -> None:
    _enter(client, "Write report", "Tend the tea")
    main = room(client)["trial"]["id"]
    assert client.post(PARALLEL, json={"source": "remaining", "ref": main}).status_code == 409


def test_an_art_and_a_horizon_item_come_down_to_run_beside(client: TestClient) -> None:
    _enter(client, "Write report")
    art = client.post("/api/arts", json={"kind": "foundational", "title": "Stretch"})
    assert art.status_code == 200
    found = client.get(f"{PARALLEL}/search", params={"q": "stretch"}).json()
    assert [(c["source"], c["type"]) for c in found] == [("art", "foundational")]
    picked = client.post(PARALLEL, json={"source": "art", "ref": found[0]["id"]}).json()
    assert picked["parallel"]["title"] == "Stretch"


def test_conquering_the_parallel_trial_leaves_the_main_one_alone(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report")
    _pick_new(client, "Tend the tea")
    client.post(f"{PARALLEL}/start")
    later(clock, 12)
    done = client.post(f"{PARALLEL}/finish", json={"how": "conquered"}).json()
    assert done["parallel"] is None
    assert done["trial"]["title"] == "Write report"
    conquered = client.get("/api/view").json()["dashboard"]["conquered"]
    assert [(c["title"], c["actual_text"]) for c in conquered] == [("Tend the tea", "12m")]
    again = _pick_new(client, "Water the plants")  # one finished, the next may run beside
    assert again["parallel"]["title"] == "Water the plants"


def test_a_parallel_mandate_is_postponed_to_the_horizon_not_abandoned(client: TestClient) -> None:
    _enter(client, "Write report")
    parallel = _pick_new(client, "Call the bank")["parallel"]["id"]
    client.patch(f"/api/trials/{parallel}", json={"is_mandate": True})
    assert client.post(f"{PARALLEL}/finish", json={"how": "abandoned"}).status_code == 409
    client.post(f"{PARALLEL}/finish", json={"how": "postponed"})
    horizon = client.get("/api/view").json()["planning"]["horizon"]
    assert [h["title"] for h in horizon] == ["Call the bank"]


def test_when_the_main_trial_ends_the_unfinished_parallel_one_is_next_with_its_state(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report", "Tend the tea", "Sweep the pavilion")
    sweep = _waiting(client, "Sweep the pavilion")
    client.post(PARALLEL, json={"source": "remaining", "ref": sweep})
    client.post(f"{PARALLEL}/start")
    later(clock, 7)
    main = room(client)["trial"]["id"]
    after = client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": main}).json()
    assert after["trial"]["title"] == "Sweep the pavilion"  # ahead of Tend the tea
    assert after["parallel"] is None
    assert _elapsed(after["trial"]) == 7 * 60  # it kept its time
    assert after["trial"]["timer"]["running"] is True  # and its state: it was running


def test_a_paused_parallel_trial_stays_paused_when_it_takes_the_ring(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report", "Tend the tea")
    _pick_new(client, "Water the plants")
    client.post(f"{PARALLEL}/start")
    later(clock, 4)
    client.post(f"{PARALLEL}/pause")
    main = room(client)["trial"]["id"]
    done = client.post("/api/seclusion/finish", json={"how": "abandoned", "trial_id": main}).json()
    assert done["trial"]["title"] == "Water the plants"
    assert (_elapsed(done["trial"]), done["trial"]["timer"]["running"]) == (4 * 60, False)


def test_stepping_out_leaves_the_parallel_trial_running_too(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report")
    _pick_new(client, "Tend the tea")
    client.post("/api/seclusion/timer/start")
    client.post(f"{PARALLEL}/start")
    later(clock, 6)
    left = client.post("/api/seclusion/leave").json()
    assert left["trial"]["timer"]["running"] is True
    assert left["parallel"]["timer"]["running"] is True
    later(clock, 4)
    assert _elapsed(room(client)["parallel"]) == 10 * 60


def test_the_parallel_trial_logs_its_own_segments(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    _enter(client, "Write report")
    parallel = _pick_new(client, "Tend the tea")["parallel"]["id"]
    client.post(f"{PARALLEL}/start")
    later(clock, 3)
    client.post(f"{PARALLEL}/pause")
    with stores() as store:
        (segment,) = store.segments.list_for_trial(parallel)
    assert (segment.discipline, segment.ended_at is not None) == (Discipline.PARALLEL, True)


def test_the_ghost_question_covers_the_parallel_timer_too(
    client: TestClient, clock: FixedClock
) -> None:
    _enter(client, "Write report")
    _pick_new(client, "Tend the tea")
    client.post(f"{PARALLEL}/start")
    later(clock, 10)
    room(client)
    later(clock, 2 * 60)
    assert client.get("/api/view").json()["ghost"] is not None
    assert _elapsed(room(client)["parallel"]) == 10 * 60
    client.post("/api/ghost/keep")
    resumed = room(client)["parallel"]
    assert (_elapsed(resumed), resumed["timer"]["running"]) == (10 * 60 + 2 * 3600, True)
