from datetime import date, datetime

from pydantic import BaseModel

from scrolly.api.schemas.dashboard import DashboardOut
from scrolly.api.schemas.knowledge import KnowledgeOut
from scrolly.api.schemas.legend import LegendOut
from scrolly.api.schemas.milestone import MilestoneOut
from scrolly.api.schemas.planning import PlanningOut
from scrolly.api.schemas.poem import PoemOut
from scrolly.domain.appearance import (
    DayVariant,
    HeaderChoice,
    Phase,
    ReadingFont,
    Theme,
)
from scrolly.domain.sky import Body
from scrolly.services.view import ViewData


class AppearanceOut(BaseModel):
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase
    serene_variant: DayVariant
    reading_font: ReadingFont
    header: HeaderChoice
    # Changes with each upload of the user's own picture, so the browser fetches it afresh.
    header_version: int


class SunsetOut(BaseModel):
    """The sunset choice. `invited` is true once the user has answered (a time, or "not now")."""

    enabled: bool
    invited: bool
    at_text: str
    chime: bool


class AdvisorOut(BaseModel):
    """The overrun advisor: `due` when the open trials would run past sunset."""

    due: bool
    mandates: int
    silenced: bool


class SoundOut(BaseModel):
    """Seclusion's sounds and the sunset chime: one volume (0-100) and one mute."""

    volume: int
    muted: bool


class GhostOut(BaseModel):
    """A timer was running while the app was away: when the user left and for how long."""

    left_text: str
    gap_text: str


class SkyOut(BaseModel):
    """The sun or the moon on Seclusion's arc: how far along its crossing (0 to 1)."""

    body: Body
    progress: float


class TravelOut(BaseModel):
    """The way up to Seclusion. `interval_min`: minutes before the full animation shows again
    (0 = every time); `welcomed`: the welcome scroll was shown; `room_focus`: a focus started in the
    room goes on."""

    interval_min: int
    welcomed: bool
    room_focus: bool


class TravelIn(BaseModel):
    """Only what is given changes."""

    interval_min: int | None = None
    welcomed: bool | None = None


class ViewOut(BaseModel):
    now: datetime
    logical_day: date
    appearance: AppearanceOut
    sunset: SunsetOut
    advisor: AdvisorOut
    # Present from the first view at dusk until the user settles it.
    poem: PoemOut | None
    legend: LegendOut
    planning: PlanningOut
    dashboard: DashboardOut
    sound: SoundOut
    sky: SkyOut
    # The cultivator meditates on the peak (domain/cultivator.py): the header looks at the summit.
    on_peak: bool = False
    travel: TravelOut
    knowledge: KnowledgeOut
    # Present until the user says whether the time away counts.
    ghost: GhostOut | None = None
    # Only the response to the day's first seal carries one.
    milestone: MilestoneOut | None = None

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
                serene_variant=a.serene_variant,
                reading_font=a.reading_font,
                header=a.header,
                header_version=a.header_version,
            ),
            sunset=SunsetOut(
                enabled=data.sunset.enabled,
                invited=data.sunset.invited,
                at_text=f"{data.sunset.hour:02d}:{data.sunset.minute:02d}",
                chime=data.sunset.chime,
            ),
            advisor=AdvisorOut(
                due=data.advisor.due,
                mandates=data.advisor.mandates,
                silenced=data.advisor.silenced,
            ),
            poem=PoemOut.from_pick(data.poem) if data.poem else None,
            legend=LegendOut.build(data.legend),
            planning=PlanningOut.from_data(
                data.planning, data.budget, data.qi, data.planning_timer
            ),
            dashboard=DashboardOut.from_data(data.dashboard),
            sound=SoundOut(volume=data.sound.volume, muted=data.sound.muted),
            sky=SkyOut(body=data.sky.body, progress=round(data.sky.progress, 3)),
            on_peak=data.on_peak,
            travel=TravelOut(
                interval_min=data.travel.interval_min,
                welcomed=data.travel.welcomed,
                room_focus=data.travel.room_focus,
            ),
            knowledge=KnowledgeOut.from_view(data.knowledge),
            ghost=None
            if data.ghost is None
            else GhostOut(left_text=data.ghost.left_text, gap_text=data.ghost.gap_text),
        )


class AppearanceIn(BaseModel):
    theme: Theme
    day_variant: DayVariant | None = None


class ReadingFontIn(BaseModel):
    font: ReadingFont


class SoundIn(BaseModel):
    """Only what is given changes."""

    volume: int | None = None
    muted: bool | None = None


class HeaderIn(BaseModel):
    choice: HeaderChoice


class SunsetIn(BaseModel):
    """Only what is given changes. A time (such as "21:00") or an on/off answers the invitation."""

    enabled: bool | None = None
    at: str | None = None
    chime: bool | None = None


class HealthOut(BaseModel):
    app: str = "scrolly"


class AdvisorIn(BaseModel):
    silenced: bool
