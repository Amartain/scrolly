from fastapi.testclient import TestClient


def test_view_shape(client: TestClient) -> None:
    body = client.get("/api/view").json()
    assert body["logical_day"] == "2026-10-18"
    assert body["appearance"] == {
        "theme": "serene",
        "day_variant": None,
        "phase": "day",
        "reading_font": "atkinson",
        "panel_style": "plaque",
        "header": "auto",
        "header_version": 0,
    }


def test_choosing_a_theme_is_returned_and_kept(client: TestClient) -> None:
    reply = client.put("/api/appearance", json={"theme": "pavilion", "day_variant": "crimson"})
    assert reply.json()["appearance"]["day_variant"] == "crimson"
    assert client.get("/api/view").json()["appearance"]["theme"] == "pavilion"


def test_unknown_theme_is_rejected(client: TestClient) -> None:
    assert client.put("/api/appearance", json={"theme": "neon"}).status_code == 422


def test_choosing_a_reading_font_is_returned_and_kept(client: TestClient) -> None:
    reply = client.put("/api/reading-font", json={"font": "opendyslexic"})
    assert reply.json()["appearance"]["reading_font"] == "opendyslexic"
    assert client.get("/api/view").json()["appearance"]["reading_font"] == "opendyslexic"


def test_unknown_reading_font_is_rejected(client: TestClient) -> None:
    assert client.put("/api/reading-font", json={"font": "comic"}).status_code == 422


def test_health_names_the_app(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"app": "scrolly"}


def test_the_view_carries_the_legend_and_each_trial_its_type(client: TestClient) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write"})
    client.post("/api/planning/proceed")
    body = client.post("/api/planning/seal").json()
    assert body["legend"]["states"]["remaining"]["shortcode"] == ":cloud:"
    assert body["legend"]["types"]["mortal"]["shortcode"] == ":white_circle:"
    assert body["dashboard"]["immediate"]["type"] == "mortal"
    assert body["planning"]["trials"][0]["type"] == "mortal"


def test_the_panel_headers_are_a_plaque_until_the_rod_is_chosen_and_kept(
    client: TestClient,
) -> None:
    assert client.get("/api/view").json()["appearance"]["panel_style"] == "plaque"
    reply = client.put("/api/panel-style", json={"style": "rod"})
    assert reply.json()["appearance"]["panel_style"] == "rod"
    assert client.get("/api/view").json()["appearance"]["panel_style"] == "rod"
    assert client.put("/api/panel-style", json={"style": "neon"}).status_code == 422
