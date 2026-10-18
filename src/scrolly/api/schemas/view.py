from datetime import date, datetime

from pydantic import BaseModel

from scrolly.api.schemas.planning import PlanningOut
from scrolly.domain.appearance import DayVariant, Phase, ReadingFont, Theme
from scrolly.services.view import ViewData


class AppearanceOut(BaseModel):
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase
    reading_font: ReadingFont


class ViewOut(BaseModel):
    now: datetime
    logical_day: date
    appearance: AppearanceOut
    planning: PlanningOut

    @classmethod
    def from_data(cls, data: ViewData) -> "ViewOut":
        a = data.appearance
        return cls(
            now=data.now,
            logical_day=data.logical_day,
            appearance=AppearanceOut(
                theme=a.theme,
                day_variant=a.day_variant,
                phase=a.phase,
                reading_font=a.reading_font,
            ),
            planning=PlanningOut.from_data(data.planning, data.budget, data.qi),
        )


class AppearanceIn(BaseModel):
    theme: Theme
    day_variant: DayVariant | None = None


class ReadingFontIn(BaseModel):
    font: ReadingFont


class HealthOut(BaseModel):
    app: str = "scrolly"
