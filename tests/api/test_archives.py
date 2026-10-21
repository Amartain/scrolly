from datetime import date, timedelta
from typing import Any

from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from scrolly.domain.models import Trial, TrialState
from scrolly.storage.store import SqliteStores
from tests.factories import make_trial

TODAY = date(2026, 10, 18)  # the logical day of the clock fixture


def _seed(stores: SqliteStores, clock: FixedClock, *trials: Trial) -> None:
    with stores() as store:
        store.trials.save(trials, clock.now())


def _past(offset: int, title: str, **fields: Any) -> Trial:
    return make_trial(title, logical_day=TODAY - timedelta(days=offset), **fields)


def test_an_empty_archive_has_no_cards(client: TestClient) -> None:
    assert client.get("/api/archives").json() == {"cards": [], "older": None}


def test_a_past_day_shows_its_essence_and_every_row(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    _seed(
        stores,
        clock,
        _past(
            1,
            "Write report",
            state=TrialState.DONE,
            essence_expected_min=60,
            essence_actual_min=75,
            completed_at=clock.now() - timedelta(days=1),
        ),
        _past(1, "Tidy desk", state=TrialState.LOST),
        _past(1, "Call back", state=TrialState.POSTPONED, is_mandate=True),
    )
    (card,) = client.get("/api/archives").json()["cards"]
    assert card["day_text"] == "Saturday, 17 October 2026"
    assert (card["actual_text"], card["expected_text"]) == ("1h15m", "1h")
    assert card["conquered"][0]["title"] == "Write report"
    assert card["conquered"][0]["actual_text"] == "1h15m"
    assert card["conquered"][0]["at_text"] == "13:12"
    assert [r["title"] for r in card["lost"]] == ["Tidy desk"]
    assert [(r["title"], r["type"]) for r in card["sent_back"]] == [("Call back", "mandate")]


def test_fourteen_days_to_a_page_then_the_older_ones(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    _seed(stores, clock, *[_past(n, f"Day {n}", state=TrialState.DONE) for n in range(1, 18)])
    first = client.get("/api/archives").json()
    assert len(first["cards"]) == 14
    assert first["cards"][0]["day"] == "2026-10-17"
    assert first["older"] == "2026-10-04"
    second = client.get("/api/archives", params={"before": first["older"]}).json()
    assert [c["day"] for c in second["cards"]] == ["2026-10-03", "2026-10-02", "2026-10-01"]
    assert second["older"] is None


def test_a_quiet_stretch_survives_a_page_boundary(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    days = [*range(1, 15), 19]
    _seed(stores, clock, *[_past(n, f"Day {n}", state=TrialState.DONE) for n in days])
    first = client.get("/api/archives").json()
    assert first["older"] == "2026-10-04"
    (last,) = client.get("/api/archives", params={"before": first["older"]}).json()["cards"]
    assert last["rest_days"] == 4  # nothing settled from 30 September to 3 October
