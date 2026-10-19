from pydantic import BaseModel

from scrolly.domain.milestones import Milestone


class MilestoneOut(BaseModel):
    """Shown once, after the day's first seal."""

    cycles: int
    banner: str | None
    quote: str
    attribution: str | None
    stand_in: bool

    @classmethod
    def from_milestone(cls, milestone: Milestone) -> "MilestoneOut":
        return cls(
            cycles=milestone.cycles,
            banner=milestone.banner,
            quote=milestone.quote.text,
            attribution=milestone.quote.attribution,
            stand_in=milestone.quote.stand_in,
        )
