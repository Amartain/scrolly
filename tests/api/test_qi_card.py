from typing import Any

from fastapi.testclient import TestClient


def _seal_and_conquer(client: TestClient, qi: str) -> str:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write report\nTidy desk"})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")
    view: dict[str, Any] = client.get("/api/view").json()
    trial_id = str(view["dashboard"]["immediate"]["id"])
    client.patch(f"/api/trials/{trial_id}", json={"qi": qi})
    client.post(f"/api/trials/{trial_id}/conquer")
    return trial_id


def test_the_card_offers_three_choices_and_the_day_as_it_would_be(client: TestClient) -> None:
    trial_id = _seal_and_conquer(client, "40")
    card = client.get(f"/api/trials/{trial_id}/qi-card", params={"qi": 60}).json()
    assert card["choices"] == {"lighter": 20, "foreseen": 40, "heavier": 60}
    assert card["spent"] == 60
    assert card["zone"] == "harmonious"
    assert 0 < card["fill_pct"] < card["calm_end_pct"] < card["surge_end_pct"] <= 100


def test_asking_saves_nothing(client: TestClient) -> None:
    trial_id = _seal_and_conquer(client, "40")
    client.get(f"/api/trials/{trial_id}/qi-card", params={"qi": 90})
    assert client.get("/api/view").json()["planning"]["qi"]["spent"] == 40


def test_a_qi_out_of_range_is_refused(client: TestClient) -> None:
    trial_id = _seal_and_conquer(client, "40")
    reply = client.get(f"/api/trials/{trial_id}/qi-card", params={"qi": 101})
    assert reply.status_code == 422
