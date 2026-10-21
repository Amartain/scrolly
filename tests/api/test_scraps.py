from fastapi.testclient import TestClient

from scrolly.clock import FixedClock
from scrolly.domain.scraps import Scrap
from scrolly.services.scraps import ScrapService
from scrolly.storage.store import SqliteStores
from tests.api.seclusion_helpers import later, room, seal

DASH = "\N{EN DASH}"


def _saved(stores: SqliteStores) -> list[Scrap]:
    with stores() as store:
        return store.scraps.list_all()


def test_what_is_written_in_seclusion_is_kept_and_comes_back(client: TestClient) -> None:
    seal(client, "Write report")
    client.post("/api/seclusion/enter")
    assert client.get("/api/scraps/current").json() == {"text": ""}
    client.put("/api/scraps/current", json={"text": "ask Sam about the invoice"})
    assert client.get("/api/scraps/current").json() == {"text": "ask Sam about the invoice"}


def test_a_scrap_records_the_visit_and_the_trials_worked_in_order(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    seal(client, "Write report", "Tidy desk")
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": "thought"})
    client.post("/api/seclusion/timer/start")
    later(clock, 5)
    first = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": first})
    client.post("/api/seclusion/timer/start")
    later(clock, 5)
    client.post("/api/seclusion/leave")
    (scrap,) = _saved(stores)
    assert scrap.closed_at == clock.now()
    assert scrap.text == "thought"
    assert len(scrap.trial_ids) == 2 and scrap.trial_ids[0] == first
    assert (scrap.closed_at - scrap.opened_at).total_seconds() == 10 * 60


def test_a_visit_with_nothing_written_leaves_no_scrap(
    client: TestClient, stores: SqliteStores
) -> None:
    seal(client, "Write report")
    client.post("/api/seclusion/enter")
    client.post("/api/seclusion/timer/start")
    client.put("/api/scraps/current", json={"text": "   "})
    client.post("/api/seclusion/leave")
    assert _saved(stores) == []


def test_a_new_visit_gets_a_new_scrap(client: TestClient, stores: SqliteStores) -> None:
    seal(client, "Write report")
    for text in ("first", "second"):
        client.post("/api/seclusion/enter")
        assert client.get("/api/scraps/current").json() == {"text": ""}
        client.put("/api/scraps/current", json={"text": text})
        client.post("/api/seclusion/leave")
    assert [s.text for s in _saved(stores)] == ["first", "second"]


def test_a_crash_closes_the_scrap_at_its_last_save(
    client: TestClient, clock: FixedClock, stores: SqliteStores
) -> None:
    seal(client, "Write report")
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": "half a thought"})
    saved_at = clock.now()
    later(clock, 6 * 60)  # the app died; the next visit finds the scrap still open
    with stores() as store:
        ScrapService(store, clock).open()
    scraps = _saved(stores)
    assert [s.text for s in scraps] == ["half a thought", ""]
    assert scraps[0].closed_at == saved_at
    assert scraps[1].is_open


def test_nothing_can_be_written_outside_seclusion(client: TestClient) -> None:
    seal(client, "Write report")
    reply = client.put("/api/scraps/current", json={"text": "stray"})
    assert reply.status_code == 409


def _visit(client: TestClient, clock: FixedClock, text: str, minutes: int = 10) -> None:
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": text})
    client.post("/api/seclusion/timer/start")
    later(clock, minutes)
    client.post("/api/seclusion/leave")


def test_the_page_lists_kept_scraps_newest_first_with_the_trials_on_a_timeline(
    client: TestClient, clock: FixedClock
) -> None:
    seal(client, "Write report", "Tidy desk")
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": "first thought"})
    client.post("/api/seclusion/timer/start")
    later(clock, 30)
    first = room(client)["trial"]["id"]
    client.post("/api/seclusion/finish", json={"how": "conquered", "trial_id": first})
    client.post("/api/seclusion/timer/start")
    later(clock, 10)
    client.post("/api/seclusion/leave")
    later(clock, 60)
    _visit(client, clock, "second thought")
    newest, oldest = client.get("/api/scraps").json()
    assert (newest["text"], oldest["text"]) == ("second thought", "first thought")
    assert oldest["day_text"] == "Sunday, 18 October 2026"
    assert (oldest["time_text"], oldest["length_text"]) == (f"13:12{DASH}13:52", "40m")
    assert [lane["title"] for lane in oldest["lanes"]] == ["Write report", "Tidy desk"]
    assert oldest["lanes"][0]["spans"] == [{"start_pct": 0.0, "width_pct": 75.0}]
    assert oldest["lanes"][1]["spans"] == [{"start_pct": 75.0, "width_pct": 25.0}]


def test_markdown_export_is_one_file_with_every_scrap_newest_first(
    client: TestClient, clock: FixedClock
) -> None:
    seal(client, "Write report")
    _visit(client, clock, "older\n\n## not a heading\n---\nstill the same scrap")
    later(clock, 60)
    _visit(client, clock, "newer", minutes=5)
    reply = client.get("/api/scraps/export.md")
    disposition = reply.headers["content-disposition"]
    assert disposition == 'attachment; filename="bamboo-scraps-2026-10-18.md"'
    text = reply.text
    assert text.startswith(f"# Bamboo Scraps\n\n## Sunday, 18 October 2026 · 14:22{DASH}14:27\n")
    assert text.index("newer") < text.index("older")
    assert "Trials: Write report" in text
    assert "## not a heading\n---\nstill the same scrap" in text


def test_a_visit_still_open_or_with_nothing_written_is_not_on_the_page(client: TestClient) -> None:
    seal(client, "Write report")
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": "still writing"})
    assert client.get("/api/scraps").json() == []
    assert client.get("/api/scraps/export.md").text == "# Bamboo Scraps\n\n\n"
