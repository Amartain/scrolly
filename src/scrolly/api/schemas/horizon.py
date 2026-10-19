from pydantic import BaseModel

from scrolly.domain.models import ArtKind


class HorizonAddIn(BaseModel):
    title: str


class HorizonPatchIn(BaseModel):
    """Only the fields that are sent change. An empty estimate clears it."""

    title: str | None = None
    estimate: str | None = None
    is_mandate: bool | None = None


class ArtOrderIn(BaseModel):
    kind: ArtKind
    ids: list[str]


class ArtAddIn(BaseModel):
    kind: ArtKind
    title: str
    estimate: str = ""


class ArtPatchIn(BaseModel):
    """Only the fields that are sent change. An empty estimate clears it."""

    title: str | None = None
    estimate: str | None = None
