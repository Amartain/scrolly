from pydantic import BaseModel

from scrolly.services.scraps_page import ScrapPage


class ScrapIn(BaseModel):
    text: str


class ScrapTextOut(BaseModel):
    """The text on the scrap of this visit to Seclusion."""

    text: str


class SpanOut(BaseModel):
    """A stretch of the visit as percentages of its length, so the screen only draws it."""

    start_pct: float
    width_pct: float


class LaneOut(BaseModel):
    title: str
    spans: list[SpanOut]


class ScrapPageOut(BaseModel):
    """One finished visit: when it was, the trials worked in the order started, and the text."""

    id: str
    day_text: str
    time_text: str
    length_text: str
    text: str
    lanes: list[LaneOut]

    @classmethod
    def from_page(cls, page: ScrapPage) -> "ScrapPageOut":
        return cls(
            id=page.id,
            day_text=page.day_text,
            time_text=page.time_text,
            length_text=page.length_text,
            text=page.text,
            lanes=[
                LaneOut(
                    title=lane.title,
                    spans=[
                        SpanOut(start_pct=s.start_pct, width_pct=s.width_pct) for s in lane.spans
                    ],
                )
                for lane in page.lanes
            ],
        )
