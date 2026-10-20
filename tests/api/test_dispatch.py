from typing import Any

from fastapi.testclient import TestClient


def _seal(client: TestClient, *titles: str) -> dict[str, Any]:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(titles)})
    client.post("/api/planning/proceed")
    sealed: dict[str, Any] = client.post("/api/planning/seal").json()
    return sealed


def test_the_scroll_is_todays_trials_in_the_owners_format(client: TestClient) -> None:
    sealed = _seal(client, "Write", "Tidy")
    client.post(f"/api/trials/{sealed['dashboard']['immediate']['id']}/conquer")
    reply = client.get("/api/dispatch").json()
    lines = reply["text"].splitlines()
    assert lines[0] == "# :scroll: Scroll of Heavenly Tribulations and Ascendent Trials"
    assert lines[2] == "18/10/2026"
    assert ":leaves: :white_circle: Write () >> 0m" in lines
    assert ":droplet: :white_circle: Tidy" in lines
    assert lines[-2:] == [":cloud: :zzz:", ":cloud: ENDE"]
    assert (reply["dnd"], reply["include_postponed"], reply["include_abandoned"]) == (
        False,
        False,
        False,
    )


def test_options_change_the_scroll_and_are_kept(client: TestClient) -> None:
    sealed = _seal(client, "Write", "Tidy")
    client.post(f"/api/trials/{sealed['dashboard']['immediate']['id']}/postpone")
    reply = client.put("/api/dispatch", json={"dnd": True, "include_postponed": True}).json()
    assert "----- NO CHECK IN DND :crescent_moon:  -----" in reply["text"]
    assert "Postponed: Write" in reply["text"]
    assert client.get("/api/dispatch").json()["dnd"] is True
    again = client.put("/api/dispatch", json={"dnd": False}).json()
    assert again["include_postponed"] is True and "DND" not in again["text"]


def test_a_custom_symbol_shows_in_the_view_and_the_scroll(client: TestClient) -> None:
    _seal(client, "Write")
    reply = client.put(
        "/api/legend",
        json={"group": "states", "key": "immediate", "emoji": "🔥", "shortcode": "fire"},
    ).json()
    assert reply["legend"]["states"]["immediate"]["emoji"] == "🔥"
    assert reply["legend"]["states"]["immediate"]["shortcode"] == ":fire:"
    assert ":fire: :white_circle: Write" in client.get("/api/dispatch").json()["text"]

    restored = client.put("/api/legend", json={"group": "states", "key": "immediate"}).json()
    assert restored["legend"]["states"]["immediate"]["emoji"] == "💧"


def test_a_symbol_already_in_use_is_refused_with_its_owner_named(client: TestClient) -> None:
    reply = client.put("/api/legend", json={"group": "states", "key": "immediate", "emoji": "🍃"})
    assert reply.status_code == 422 and "Conquered" in reply.json()["detail"]
    assert client.get("/api/view").json()["legend"]["states"]["immediate"]["emoji"] == "💧"
