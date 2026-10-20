from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def _upload(client: TestClient, name: str, content: bytes) -> object:
    return client.post("/api/header-image", files={"file": (name, content, "image/png")})


def test_the_default_header_follows_the_theme(client: TestClient) -> None:
    appearance = client.get("/api/view").json()["appearance"]
    assert (appearance["header"], appearance["header_version"]) == ("auto", 0)


def test_a_built_in_picture_can_be_chosen_and_the_theme_default_restored(
    client: TestClient,
) -> None:
    chosen = client.put("/api/header", json={"choice": "serene-dusk"}).json()
    assert chosen["appearance"]["header"] == "serene-dusk"
    # Changing the theme keeps the header picture.
    themed = client.put("/api/appearance", json={"theme": "pavilion"}).json()
    assert themed["appearance"]["header"] == "serene-dusk"
    restored = client.put("/api/header", json={"choice": "auto"}).json()
    assert restored["appearance"]["header"] == "auto"


def test_the_users_own_picture_cannot_be_chosen_before_it_is_uploaded(client: TestClient) -> None:
    reply = client.put("/api/header", json={"choice": "custom"})
    assert reply.status_code == 422 and "picture of your own" in reply.json()["detail"]
    assert client.get("/api/header-image").status_code == 404


def test_an_uploaded_picture_becomes_the_header_and_is_served_back(
    app_client: TestClient,
) -> None:
    reply = _upload(app_client, "mine.png", PNG)
    appearance = reply.json()["appearance"]  # type: ignore[attr-defined]
    assert (appearance["header"], appearance["header_version"]) == ("custom", 1)
    served = app_client.get("/api/header-image")
    assert served.status_code == 200
    assert served.headers["content-type"] == "image/png" and served.content == PNG

    # Choosing a built-in picture keeps the upload for later.
    app_client.put("/api/header", json={"choice": "pavilion"})
    assert app_client.get("/api/header-image").content == PNG
    assert app_client.put("/api/header", json={"choice": "custom"}).status_code == 200
    # A second upload is a new version, and the old file is gone.
    second = _upload(app_client, "again.png", PNG + b"2").json()  # type: ignore[attr-defined]
    assert second["appearance"]["header_version"] == 2
    assert app_client.get("/api/header-image").content == PNG + b"2"


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        pytest.param(b"GIF89a....", "PNG, JPEG or WebP", id="gif"),
        pytest.param(b"", "empty", id="empty"),
        pytest.param(PNG + b"\x00" * (6 * 1024 * 1024), "5 MB", id="too-big"),
    ],
)
def test_a_wrong_upload_is_refused_and_nothing_changes(
    app_client: TestClient,
    content: bytes,
    reason: str,
    copies: Path,
) -> None:
    reply = _upload(app_client, "mine.gif", content)
    assert reply.status_code == 422 and reason in reply.json()["detail"]  # type: ignore[attr-defined]
    assert app_client.get("/api/view").json()["appearance"]["header"] == "auto"
    assert not list(copies.parent.glob("header-image.*"))
