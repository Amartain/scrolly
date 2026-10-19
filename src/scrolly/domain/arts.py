"""Adding, editing and removing Arts. Pure: each function checks the rule and returns the result.

An Art is a practice. Its title is unique within its own list (see `uniqueness`), its duration
follows the time format, and summoning it makes a new trial each time.
"""

from collections.abc import Sequence
from dataclasses import replace

from scrolly.domain.duration import parse_duration
from scrolly.domain.models import Art, ArtKind
from scrolly.domain.uniqueness import require_free_art_title


class ArtError(ValueError):
    """A change to the Arts that cannot be made. The message is shown to the user."""


def _title(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ArtError("An Art needs a title")
    return cleaned


def _find(arts: Sequence[Art], art_id: str) -> Art:
    art = next((a for a in arts if a.id == art_id), None)
    if art is None:
        raise ArtError("That Art no longer exists")
    return art


def add(arts: Sequence[Art], art_id: str, kind: ArtKind, title: str, estimate: str = "") -> Art:
    cleaned = _title(title)
    require_free_art_title(cleaned, arts, kind)
    return Art(id=art_id, kind=kind, title=cleaned, essence_expected_min=parse_duration(estimate))


def edit(
    arts: Sequence[Art], art_id: str, title: str | None = None, estimate: str | None = None
) -> Art:
    """Only the fields that are given change. A blank estimate clears the duration."""
    art = _find(arts, art_id)
    if title is not None:
        cleaned = _title(title)
        require_free_art_title(cleaned, arts, art.kind, except_id=art_id)
        art = replace(art, title=cleaned)
    if estimate is not None:
        art = replace(art, essence_expected_min=parse_duration(estimate))
    return art


def remove(arts: Sequence[Art], art_id: str) -> Art:
    """The Art to delete. Trials already summoned from it stay on their scrolls."""
    return _find(arts, art_id)
