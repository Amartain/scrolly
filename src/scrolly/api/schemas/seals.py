from pydantic import BaseModel

from scrolly.api.schemas.view import ViewOut


class SealIn(BaseModel):
    text: str


class SealOut(BaseModel):
    """`recognized` is false when the words name no seal; nothing changed then."""

    recognized: bool
    view: ViewOut
