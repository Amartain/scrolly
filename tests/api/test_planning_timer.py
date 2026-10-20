from datetime import datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock


def _timer(view: dict[str, Any]) -> tuple[int, bool]:
    timer = view["planning"]["timer"]
    return timer["elapsed_s"], timer["running"]


def test_a_new_day_has_a_quiet_zero_timer(client: TestClient) -> None:
    view = client.get("/api/view").json()
    assert _timer(view) == (0, False)
    assert view["planning"]["timer"]["expected_s"] is None


def test_it_counts_from_its_start_across_long_gaps(client: TestClient, clock: FixedClock) -> None:
    client.post("/api/planning/start")
    assert _timer(client.post("/api/planning/timer/start").json()) == (0, True)
    clock.set(clock.now() + timedelta(minutes=12))
    assert _timer(client.get("/api/view").json()) == (720, True)
    paused = client.post("/api/planning/timer/pause").json()
    assert _timer(paused) == (720, False)
    clock.set(clock.now() + timedelta(hours=3))
    assert _timer(client.get("/api/view").json()) == (720, False)


def test_a_second_stretch_adds_and_reset_zeroes(client: TestClient, clock: FixedClock) -> None:
    client.post("/api/planning/timer/start")
    clock.set(clock.now() + timedelta(minutes=5))
    client.post("/api/planning/timer/pause")
    client.post("/api/planning/timer/start")
    clock.set(clock.now() + timedelta(minutes=2))
    assert _timer(client.get("/api/view").json()) == (420, True)
    assert _timer(client.post("/api/planning/timer/reset").json()) == (0, False)


def test_sealing_banks_a_running_timer(client: TestClient, clock: FixedClock) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write"})
    client.post("/api/planning/proceed")
    client.post("/api/planning/timer/start")
    clock.set(clock.now() + timedelta(minutes=9))
    sealed = client.post("/api/planning/seal").json()
    assert _timer(sealed) == (540, False)
    clock.set(clock.now() + timedelta(hours=1))
    assert _timer(client.get("/api/view").json()) == (540, False)


def test_planning_time_is_recorded_per_day_in_the_backup(client: TestClient) -> None:
    import csv
    import io
    import zipfile

    client.post("/api/planning/timer/start")
    client.post("/api/planning/timer/pause")
    archive = zipfile.ZipFile(io.BytesIO(client.get("/api/export").content))
    rows = list(csv.DictReader(io.StringIO(archive.read("day.csv").decode())))
    assert "planning_accumulated_s" in rows[0] and "planning_started_at" in rows[0]


def test_a_timer_left_running_overnight_is_closed_at_the_end_of_its_day(
    client: TestClient, clock: FixedClock
) -> None:
    clock.set(datetime.fromisoformat("2026-10-18T23:30:00+02:00"))
    client.post("/api/planning/timer/start")
    clock.set(datetime.fromisoformat("2026-10-19T09:00:00+02:00"))
    today = client.get("/api/view").json()
    assert _timer(today) == (0, False)  # the new day starts with its own, quiet timer
    clock.set(datetime.fromisoformat("2026-10-18T23:45:00+02:00"))
    # The earlier day holds the time until its end (04:00): 4h30m since 23:30.
    yesterday = client.get("/api/view").json()
    assert _timer(yesterday) == (4 * 3600 + 30 * 60, False)
