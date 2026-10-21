"""Correcting the time a conquered trial took, on the dashboard."""

from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from tests.api.seclusion_helpers import later, seal


def _dashboard(client: TestClient) -> dict[str, Any]:
    dashboard: dict[str, Any] = client.get("/api/view").json()["dashboard"]
    return dashboard


def _conquer_after(client: TestClient, clock: FixedClock, minutes: int) -> str:
    trial_id = str(_dashboard(client)["immediate"]["id"])
    client.post(f"/api/trials/{trial_id}/timer/start")
    later(clock, minutes)
    client.post(f"/api/trials/{trial_id}/conquer")
    return trial_id


def test_a_conquered_trials_time_is_corrected_and_essence_follows(
    client: TestClient, clock: FixedClock
) -> None:
    seal(client, "Write report", "Tidy desk")
    trial_id = _conquer_after(client, clock, 27)
    assert _dashboard(client)["essence"]["actual_text"] == "27m"
    view = client.put(f"/api/trials/{trial_id}/actual", json={"text": "45m"})
    assert view.status_code == 200
    dashboard = view.json()["dashboard"]
    assert dashboard["conquered"][0]["actual_text"] == "45m"
    assert dashboard["essence"]["actual_text"] == "45m"


def test_a_revived_trial_carries_on_from_the_corrected_time(
    client: TestClient, clock: FixedClock
) -> None:
    seal(client, "Write report")
    trial_id = _conquer_after(client, clock, 27)
    client.put(f"/api/trials/{trial_id}/actual", json={"text": "1h5m"})
    client.post(f"/api/trials/{trial_id}/revive")
    assert _dashboard(client)["immediate"]["timer"]["elapsed_s"] == 65 * 60


def test_a_time_that_cannot_be_used_is_refused_and_the_old_one_stays(
    client: TestClient, clock: FixedClock
) -> None:
    seal(client, "Write report", "Tidy desk")
    trial_id = _conquer_after(client, clock, 27)
    assert client.put(f"/api/trials/{trial_id}/actual", json={"text": "soon"}).status_code == 422
    waiting = str(_dashboard(client)["immediate"]["id"])
    assert client.put(f"/api/trials/{waiting}/actual", json={"text": "5m"}).status_code == 409
    assert _dashboard(client)["conquered"][0]["actual_text"] == "27m"
