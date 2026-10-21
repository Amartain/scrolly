from fastapi.testclient import TestClient

from tests.api.seclusion_helpers import room, seal


def test_bamboo_scraps_is_shown_until_it_is_hidden(client: TestClient) -> None:
    assert room(client)["scraps_hidden"] is False
    seal(client, "Write")
    client.post("/api/seclusion/enter")
    assert room(client)["scraps_hidden"] is False


def test_hiding_it_is_kept_and_showing_it_again_undoes_it(client: TestClient) -> None:
    seal(client, "Write")
    client.post("/api/seclusion/enter")
    hidden = client.put("/api/seclusion/scraps-hidden", json={"hidden": True})
    assert hidden.status_code == 200
    assert hidden.json()["scraps_hidden"] is True
    # Stepping out and coming back does not bring it back: it is the user's choice, not the visit's.
    client.post("/api/seclusion/leave")
    client.post("/api/seclusion/enter")
    assert room(client)["scraps_hidden"] is True
    shown = client.put("/api/seclusion/scraps-hidden", json={"hidden": False})
    assert shown.json()["scraps_hidden"] is False
    assert room(client)["scraps_hidden"] is False


def test_hiding_scraps_leaves_the_scrap_alone(client: TestClient) -> None:
    seal(client, "Write")
    client.post("/api/seclusion/enter")
    client.put("/api/scraps/current", json={"text": "a loose thought"})
    client.put("/api/seclusion/scraps-hidden", json={"hidden": True})
    assert client.get("/api/scraps/current").json()["text"] == "a loose thought"
