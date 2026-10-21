from typing import Literal

from pydantic import BaseModel

from scrolly.domain.legend import TrialType
from scrolly.domain.parallel import Candidate, Source


class CandidateOut(BaseModel):
    """Something the search bar offers to run beside the trial at hand."""

    source: Source
    id: str
    title: str
    type: TrialType

    @classmethod
    def from_candidate(cls, found: Candidate) -> "CandidateOut":
        return cls(source=found.source, id=found.id, title=found.title, type=found.type)


class ParallelPickIn(BaseModel):
    """A waiting trial, an Art or a Horizon item by id, or (`new`) a title to make on the spot."""

    source: Source | Literal["new"]
    ref: str


class ParallelFinishIn(BaseModel):
    how: Literal["conquered", "abandoned", "postponed"]
