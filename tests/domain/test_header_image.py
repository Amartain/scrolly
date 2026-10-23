import pytest

from scrolly.domain.appearance import (
    AppearanceError,
    HeaderChoice,
    Preferences,
    choose_header,
    read_header_choice,
    resolve_appearance,
    with_uploaded_header,
)
from scrolly.domain.header_image import MAX_BYTES, HeaderImageError, sniff_image

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 20
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 20


def test_png_jpeg_and_webp_are_told_by_their_first_bytes() -> None:
    assert sniff_image(PNG).extension == "png"
    assert sniff_image(JPEG).media_type == "image/jpeg"
    assert sniff_image(WEBP).media_type == "image/webp"


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        pytest.param(b"", "empty", id="empty"),
        pytest.param(b"GIF89a" + b"\x00" * 20, "PNG, JPEG or WebP", id="gif"),
        pytest.param(b"<svg></svg>", "PNG, JPEG or WebP", id="svg"),
        pytest.param(PNG + b"\x00" * MAX_BYTES, "5 MB", id="too-big"),
    ],
)
def test_other_files_are_refused_with_a_reason(content: bytes, reason: str) -> None:
    with pytest.raises(HeaderImageError, match=reason):
        sniff_image(content)


def test_the_header_follows_the_theme_until_a_picture_is_chosen() -> None:
    assert Preferences().header is HeaderChoice.AUTO
    assert resolve_appearance(Preferences()).header is HeaderChoice.AUTO


def test_the_users_own_picture_needs_an_upload_first() -> None:
    with pytest.raises(AppearanceError, match="picture of your own"):
        choose_header(Preferences(), HeaderChoice.CUSTOM)
    uploaded = with_uploaded_header(Preferences())
    assert (uploaded.header, uploaded.header_version) == (HeaderChoice.CUSTOM, 1)
    assert choose_header(uploaded, HeaderChoice.AUTO).header is HeaderChoice.AUTO
    # Going back to it later works, and a second upload is a new version.
    assert choose_header(uploaded, HeaderChoice.AUTO).header_version == 1
    assert with_uploaded_header(uploaded).header_version == 2


@pytest.mark.parametrize("saved", ["serene-day", "serene-dusk", "pavilion", "auto", None, "odd"])
def test_a_retired_built_in_picture_reads_as_the_peak(saved: str | None) -> None:
    assert read_header_choice(saved) is HeaderChoice.AUTO


def test_the_users_own_picture_reads_as_itself() -> None:
    assert read_header_choice("custom") is HeaderChoice.CUSTOM
