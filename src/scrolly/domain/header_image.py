"""The header picture the user may upload: what counts as one. Pure."""

from dataclasses import dataclass

MAX_BYTES = 5 * 1024 * 1024


class HeaderImageError(ValueError):
    """An upload that cannot be used as a header picture. The message is shown to the user."""


@dataclass(frozen=True)
class ImageKind:
    extension: str
    media_type: str


def sniff_image(content: bytes) -> ImageKind:
    """PNG, JPEG or WebP, told by the first bytes (not by the file name), up to 5 MB."""
    if not content:
        raise HeaderImageError("That file is empty")
    if len(content) > MAX_BYTES:
        raise HeaderImageError("That picture is larger than 5 MB")
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ImageKind("png", "image/png")
    if content.startswith(b"\xff\xd8\xff"):
        return ImageKind("jpg", "image/jpeg")
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ImageKind("webp", "image/webp")
    raise HeaderImageError("Use a PNG, JPEG or WebP picture")
