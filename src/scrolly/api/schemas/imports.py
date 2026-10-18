from pydantic import BaseModel

from scrolly.api.schemas.view import ViewOut
from scrolly.domain.merge import ImportSummary
from scrolly.services.view import ViewData


class ImportOut(BaseModel):
    added: int
    skipped: int
    trials_added: int
    horizon_added: int
    arts_added: int
    view: ViewOut

    @classmethod
    def from_data(cls, summary: ImportSummary, view: ViewData) -> "ImportOut":
        return cls(
            added=summary.added,
            skipped=summary.skipped,
            trials_added=summary.trials_added,
            horizon_added=summary.horizon_added,
            arts_added=summary.arts_added,
            view=ViewOut.from_data(view),
        )
