from datetime import datetime
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _view(client: TestClient) -> dict[str, Any]:
    view: dict[str, Any] = client.get("/api/view").json()
    return view


def _seal(client: TestClient, *titles: str) -> dict[str, Any]:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    sealed: dict[str, Any] = client.post("/api/planning/seal").json()
    return sealed


def test_before_the_invitation_is_answered_nothing_changes_colour(client: TestClient) -> None:
    view = _view(client)
    assert view["sunset"] == {
        "enabled": False,
        "invited": False,
        "at_text": "21:00",
        "chime": False,
    }
    assert view["appearance"]["phase"] == "day"
    assert view["planning"]["budget"]["has_sunset"] is True


def test_answering_with_a_time_turns_the_sunset_on(client: TestClient) -> None:
    reply = client.put("/api/sunset", json={"at": "19:30"}).json()
    assert reply["sunset"] == {"enabled": True, "invited": True, "at_text": "19:30", "chime": False}


def test_not_now_keeps_the_day_summary_to_totals(client: TestClient) -> None:
    reply = client.put("/api/sunset", json={"enabled": False}).json()
    assert reply["sunset"]["invited"] is True and reply["sunset"]["enabled"] is False
    assert reply["planning"]["budget"]["has_sunset"] is False
    assert reply["planning"]["budget"]["light_text"] is None


def test_an_unreadable_time_is_refused_and_not_saved(client: TestClient) -> None:
    reply = client.put("/api/sunset", json={"at": "9pm"})
    assert reply.status_code == 422 and "21:00" in reply.json()["detail"]
    assert _view(client)["sunset"]["invited"] is False


def test_the_chime_is_its_own_choice(client: TestClient) -> None:
    client.put("/api/sunset", json={"at": "21:00"})
    reply = client.put("/api/sunset", json={"chime": True}).json()
    assert reply["sunset"]["chime"] is True and reply["sunset"]["at_text"] == "21:00"


def test_the_palette_warms_then_turns_to_dusk_by_the_clock(
    client: TestClient, clock: FixedClock
) -> None:
    client.put("/api/sunset", json={"at": "21:00"})
    phases = []
    for moment in ("19:00", "20:15", "21:05"):
        clock.set(datetime.fromisoformat(f"2026-10-18T{moment}:00+02:00"))
        phases.append(_view(client)["appearance"]["phase"])
    assert phases == ["day", "golden", "dusk"]


def test_finishing_the_day_brings_dusk_even_with_no_sunset(client: TestClient) -> None:
    client.put("/api/sunset", json={"enabled": False})
    sealed = _seal(client, "Only trial")
    assert sealed["appearance"]["phase"] == "day"
    trial_id = sealed["dashboard"]["immediate"]["id"]
    done = client.post(f"/api/trials/{trial_id}/conquer").json()
    assert done["appearance"]["phase"] == "dusk"


def test_dusk_stays_after_a_new_trial_is_scribed(client: TestClient) -> None:
    sealed = _seal(client, "Only trial")
    trial_id = sealed["dashboard"]["immediate"]["id"]
    client.post(f"/api/trials/{trial_id}/conquer")
    scribed = client.post("/api/trials", json={"title": "One more"}).json()
    assert scribed["appearance"]["phase"] == "dusk"


def test_a_day_with_trials_left_stays_in_daylight(client: TestClient) -> None:
    sealed = _seal(client, "First", "Second")
    trial_id = sealed["dashboard"]["immediate"]["id"]
    assert client.post(f"/api/trials/{trial_id}/conquer").json()["appearance"]["phase"] == "day"


def test_the_poem_comes_at_dusk_once_a_day(client: TestClient, clock: FixedClock) -> None:
    client.put("/api/sunset", json={"at": "21:00"})
    assert _view(client)["poem"] is None
    clock.set(datetime.fromisoformat("2026-10-18T21:05:00+02:00"))
    first = _view(client)["poem"]
    assert first is not None and first["stand_in"] is True and len(first["chinese"]) == 2
    assert _view(client)["poem"] == first  # a reload shows the same page

    settled = client.post("/api/sunset/poem-seen").json()
    assert settled["poem"] is None
    assert _view(client)["poem"] is None

    clock.set(datetime.fromisoformat("2026-10-19T21:05:00+02:00"))
    assert _view(client)["poem"] is not None  # the next day's dusk has its own


def test_finishing_the_day_brings_the_poem_too(client: TestClient) -> None:
    client.put("/api/sunset", json={"enabled": False})
    sealed = _seal(client, "Only trial")
    assert sealed["poem"] is None
    done = client.post(f"/api/trials/{sealed['dashboard']['immediate']['id']}/conquer").json()
    assert done["poem"] is not None
