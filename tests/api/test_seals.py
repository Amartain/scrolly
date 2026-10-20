from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _seal(client: TestClient, *titles: str) -> dict[str, Any]:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    sealed: dict[str, Any] = client.post("/api/planning/seal").json()
    return sealed


def _words(client: TestClient, text: str) -> dict[str, Any]:
    reply: dict[str, Any] = client.post("/api/seal-inscription", json={"text": text}).json()
    return reply


def test_unknown_words_do_nothing(client: TestClient) -> None:
    _seal(client, "Write")
    reply = _words(client, "open sesame")
    assert reply["recognized"] is False
    assert reply["view"]["planning"]["status"] == "active"


def test_dusk_forces_the_palette_and_brings_the_poem_back_and_sunrise_clears_it(
    client: TestClient,
) -> None:
    _seal(client, "Write", "Tidy")
    dusk = _words(client, "dusk")
    assert dusk["recognized"] and dusk["view"]["appearance"]["phase"] == "dusk"
    assert dusk["view"]["poem"] is not None
    client.post("/api/sunset/poem-seen")
    assert client.get("/api/view").json()["poem"] is None
    again = _words(client, "Dusk")  # the poem may be read again
    assert again["view"]["poem"] is not None
    sunrise = _words(client, "sunrise")
    assert sunrise["view"]["appearance"]["phase"] == "day"


def test_a_day_number_returns_that_days_milestone(client: TestClient) -> None:
    ten = _words(client, "day 10")
    assert ten["recognized"]
    assert (ten["view"]["milestone"]["cycles"], ten["view"]["milestone"]["banner"]) == (
        10,
        "Day 10 Milestone: Foundation Established!",
    )
    assert _words(client, "21")["view"]["milestone"]["cycles"] == 21
    assert _words(client, "arise")["view"]["milestone"]["quote"] == "Arise."


def test_the_4am_seal_settles_todays_open_trials_like_the_rollover(client: TestClient) -> None:
    sealed = _seal(client, "Mortal one", "Mandate one", "Mortal two")
    mandate = next(t for t in sealed["planning"]["trials"] if t["title"] == "Mandate one")
    client.patch(f"/api/trials/{mandate['id']}", json={"is_mandate": True})
    client.put("/api/sunset", json={"at": "21:00"})

    reply = _words(client, "4AM")
    view = reply["view"]
    assert view["planning"]["trials"] == []
    assert [h["title"] for h in view["planning"]["horizon"]] == ["Mandate one"]
    fallen = {t["title"] for t in view["dashboard"]["lost"]}
    assert fallen == {"Mortal one", "Mortal two"}
    # Said twice, nothing more happens.
    assert _words(client, "4am")["view"]["planning"]["horizon"] == view["planning"]["horizon"]


def test_restart_today_returns_to_the_zero_state_and_keeps_a_copy(
    app_client: TestClient, copies: Path
) -> None:
    sealed = _seal(app_client, "Write", "Tidy")
    app_client.post(f"/api/trials/{sealed['dashboard']['immediate']['id']}/conquer")
    app_client.post("/api/horizon", json={"title": "An idea"})
    horizon_id = app_client.get("/api/view").json()["planning"]["horizon"][0]["id"]
    app_client.post("/api/trials/summon", json={"source": "horizon", "id": horizon_id})

    reply = _words(app_client, "restart-today")
    view = reply["view"]
    assert reply["recognized"] and view["planning"]["status"] == "zero"
    assert view["planning"]["trials"] == [] and view["dashboard"]["conquered"] == []
    assert view["dashboard"]["heavenly_cycles"] == 0
    assert [h["title"] for h in view["planning"]["horizon"]] == ["An idea"]
    assert len(list(copies.glob("scrolly-before-restart-*.zip"))) == 1


def test_after_a_restart_the_day_can_be_planned_and_sealed_again(client: TestClient) -> None:
    _seal(client, "First attempt")
    _words(client, "restart-today")
    again = _seal(client, "Second attempt")
    assert again["planning"]["status"] == "active"
    assert again["dashboard"]["immediate"]["title"] == "Second attempt"
    assert again["dashboard"]["heavenly_cycles"] == 1


def test_restart_keeps_the_rollover_done_and_other_days_untouched(
    client: TestClient, clock: FixedClock
) -> None:
    _seal(client, "Yesterday's work")
    clock.set(datetime.fromisoformat("2026-10-19T10:00:00+02:00"))
    client.get("/api/view")
    _words(client, "restart-today")
    clock.set(datetime.fromisoformat("2026-10-18T13:00:00+02:00"))
    # The earlier day still stands as it was: its trial was lost to time by the rollover.
    # The restart only reached the logical day it was inscribed on (the 19th).
    assert client.get("/api/view").json()["dashboard"]["heavenly_cycles"] == 1
