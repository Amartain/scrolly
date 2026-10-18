from datetime import date, datetime

from pydantic import BaseModel

from scrolly.domain.appearance import DayVariant, Phase, Theme
from scrolly.services.view import ViewData


class AppearanceOut(BaseModel):
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase


class ViewOut(BaseModel):
    now: datetime
    logical_day: date
    appearance: AppearanceOut

    @classmethod
    def from_data(cls, data: ViewData) -> "ViewOut":
        a = data.appearance
        return cls(
            now=data.now,
            logical_day=data.logical_day,
            appearance=AppearanceOut(theme=a.theme, day_variant=a.day_variant, phase=a.phase),
        )


class AppearanceIn(BaseModel):
    theme: Theme
    day_variant: DayVariant | None = None


class HealthOut(BaseModel):
    app: str = "scrolly"
