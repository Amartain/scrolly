from typing import Any

from fastapi.testclient import TestClient


def _items(client: TestClient) -> list[dict[str, Any]]:
    view: dict[str, Any] = client.get("/api/view").json()
    items: list[dict[str, Any]] = view["planning"]["horizon"]
    return items


def test_a_horizon_estimate_is_set_once(client: TestClient) -> None:
    client.post("/api/horizon", json={"title": "Garden"})
    item_id = _items(client)[0]["id"]
    assert client.patch(f"/api/horizon/{item_id}", json={"estimate": "45m"}).status_code == 200
    for attempt in ("1h", ""):
        refused = client.patch(f"/api/horizon/{item_id}", json={"estimate": attempt})
        assert refused.status_code == 409
        assert "already set" in refused.text
    assert _items(client)[0]["expected_text"] == "45m"


def test_renaming_a_horizon_item_keeps_its_estimate(client: TestClient) -> None:
    client.post("/api/horizon", json={"title": "Garden", "estimate": "45m"})
    item_id = _items(client)[0]["id"]
    assert client.patch(f"/api/horizon/{item_id}", json={"title": "Weed"}).status_code == 200
    assert [(i["title"], i["expected_text"]) for i in _items(client)] == [("Weed", "45m")]
