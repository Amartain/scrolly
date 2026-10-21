from datetime import date

from pydantic import BaseModel

from scrolly.domain.legend import TrialType
from scrolly.services.archives_view import ArchiveCard, ArchivePage, ArchiveRow


class ArchiveRowOut(BaseModel):
    id: str
    title: str
    type: TrialType
    expected_text: str
    actual_text: str
    qi_text: str
    at_text: str

    @classmethod
    def from_row(cls, row: ArchiveRow) -> "ArchiveRowOut":
        return cls(
            id=row.id,
            title=row.title,
            type=row.type,
            expected_text=row.expected_text,
            actual_text=row.actual_text,
            qi_text=row.qi_text,
            at_text=row.at_text,
        )


class ArchiveCardOut(BaseModel):
    """One past day: its Essence, the quiet days before it, and what became of each trial."""

    day: date
    day_text: str
    actual_text: str
    expected_text: str
    rest_days: int
    conquered: list[ArchiveRowOut]
    lost: list[ArchiveRowOut]
    sent_back: list[ArchiveRowOut]

    @classmethod
    def from_card(cls, card: ArchiveCard) -> "ArchiveCardOut":
        return cls(
            day=card.day,
            day_text=card.day_text,
            actual_text=card.actual_text,
            expected_text=card.expected_text,
            rest_days=card.rest_days,
            conquered=[ArchiveRowOut.from_row(r) for r in card.conquered],
            lost=[ArchiveRowOut.from_row(r) for r in card.lost],
            sent_back=[ArchiveRowOut.from_row(r) for r in card.sent_back],
        )


class ArchivePageOut(BaseModel):
    cards: list[ArchiveCardOut]
    older: date | None

    @classmethod
    def from_page(cls, page: ArchivePage) -> "ArchivePageOut":
        return cls(cards=[ArchiveCardOut.from_card(c) for c in page.cards], older=page.older)
