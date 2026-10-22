from pydantic import BaseModel

from scrolly.api.schemas.dashboard import VictoryOut
from scrolly.api.schemas.view import ViewOut


class SealIn(BaseModel):
    text: str


class SealOut(BaseModel):
    """`recognized` is false when the words name no seal; nothing changed then.

    `victory_preview` is the finished-day ceremony a seal asked to see once (it changes nothing)."""

    recognized: bool
    view: ViewOut
    victory_preview: VictoryOut | None = None
