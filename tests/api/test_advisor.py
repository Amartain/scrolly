from datetime import datetime
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _ready(client: TestClient, clock: FixedClock, *lines: str) -> dict[str, Any]:
    """Sunset at 21:00, a sealed day with the given dump lines, and the clock at 19:00."""
    client.put("/api/sunset", json={"at": "21:00"})
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "\n".join(lines)})
    reply = client.post("/api/planning/proceed").json()
    for trial in reply["planning"]["trials"]:
        client.patch(f"/api/planning/trials/{trial['id']}", json={"estimate": "1h"})
    client.post("/api/planning/seal")
    clock.set(datetime.fromisoformat("2026-10-18T19:00:00+02:00"))
    view: dict[str, Any] = client.get("/api/view").json()
    return view


def _make_mandate(client: TestClient, title: str) -> None:
    view = client.get("/api/view").json()
    trial = next(t for t in view["planning"]["trials"] if t["title"] == title)
    client.patch(f"/api/trials/{trial['id']}", json={"is_mandate": True})


def test_the_advisor_is_due_when_the_open_trials_run_past_sunset(
    client: TestClient, clock: FixedClock
) -> None:
    view = _ready(client, clock, "A", "B", "C")  # three hours, two left before sunset
    assert view["advisor"]["due"] is True


def test_it_stays_quiet_when_the_plan_fits(client: TestClient, clock: FixedClock) -> None:
    assert _ready(client, clock, "A", "B")["advisor"]["due"] is False


def test_not_again_today_survives_a_reload_and_can_be_undone(
    client: TestClient, clock: FixedClock
) -> None:
    _ready(client, clock, "A", "B", "C")
    silenced = client.put("/api/advisor", json={"silenced": True}).json()
    assert (silenced["advisor"]["due"], silenced["advisor"]["silenced"]) == (False, True)
    assert client.get("/api/view").json()["advisor"]["due"] is False
    woken = client.put("/api/advisor", json={"silenced": False}).json()
    assert woken["advisor"]["due"] is True


def test_postponing_mandates_keeps_the_immediate_trial(
    client: TestClient, clock: FixedClock
) -> None:
    _ready(client, clock, "A", "B", "C")
    _make_mandate(client, "B")
    view = client.get("/api/view").json()
    assert view["advisor"]["mandates"] == 1
    immediate_title = view["dashboard"]["immediate"]["title"]

    after = client.post("/api/advisor/postpone-mandates").json()
    assert after["dashboard"]["immediate"]["title"] == immediate_title
    waiting = [t["title"] for t in after["planning"]["trials"] if t["state"] == "remaining"]
    assert waiting == ["C"]
    assert [i["title"] for i in after["planning"]["horizon"]] == ["B"]
    assert after["advisor"]["due"] is False  # said once for the day
