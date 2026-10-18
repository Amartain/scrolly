from fastapi.testclient import TestClient


def test_view_shape(client: TestClient) -> None:
    body = client.get("/api/view").json()
    assert body["logical_day"] == "2026-10-18"
    assert body["appearance"] == {"theme": "serene", "day_variant": None, "phase": "day"}


def test_choosing_a_theme_is_returned_and_kept(client: TestClient) -> None:
    reply = client.put("/api/appearance", json={"theme": "pavilion", "day_variant": "crimson"})
    assert reply.json()["appearance"]["day_variant"] == "crimson"
    assert client.get("/api/view").json()["appearance"]["theme"] == "pavilion"


def test_unknown_theme_is_rejected(client: TestClient) -> None:
    assert client.put("/api/appearance", json={"theme": "neon"}).status_code == 422


def test_health_names_the_app(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"app": "scrolly"}
