from pydantic import BaseModel

from scrolly.domain.dispatch import DispatchOptions


class DispatchOut(BaseModel):
    """The scroll as text for Discord, with the options that shaped it."""

    text: str
    dnd: bool
    include_postponed: bool
    include_abandoned: bool

    @classmethod
    def build(cls, text: str, options: DispatchOptions) -> "DispatchOut":
        return cls(
            text=text,
            dnd=options.dnd,
            include_postponed=options.include_postponed,
            include_abandoned=options.include_abandoned,
        )


class DispatchIn(BaseModel):
    """Only what is given changes."""

    dnd: bool | None = None
    include_postponed: bool | None = None
    include_abandoned: bool | None = None


class SymbolIn(BaseModel):
    """One symbol of the Legend. Give neither emoji nor shortcode to restore the default."""

    group: str
    key: str
    emoji: str | None = None
    shortcode: str | None = None
