"""The user's own header picture, kept as a file beside the database."""

from pathlib import Path

from scrolly.domain.header_image import ImageKind

_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}


class HeaderFile:
    def __init__(self, folder: Path | None) -> None:
        self._folder = folder

    def save(self, content: bytes, kind: ImageKind) -> None:
        """Keep this picture, and only this one."""
        if self._folder is None:
            return
        self._folder.mkdir(parents=True, exist_ok=True)
        for old in self._folder.glob("header-image.*"):
            old.unlink()
        (self._folder / f"header-image.{kind.extension}").write_bytes(content)

    def read(self) -> tuple[bytes, str] | None:
        """The picture and its media type, or None if there is none."""
        if self._folder is None:
            return None
        for extension, media_type in _TYPES.items():
            path = self._folder / f"header-image.{extension}"
            if path.is_file():
                return path.read_bytes(), media_type
        return None
