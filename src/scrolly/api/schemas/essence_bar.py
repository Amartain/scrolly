from pydantic import BaseModel

from scrolly.domain.duration import format_duration
from scrolly.domain.essence import EssenceBar


class EssenceBarOut(BaseModel):
    """The Essence bar's shares of one scale, and the light left (None without a sunset)."""

    done_pct: float
    plan_pct: float
    sunset_pct: float | None
    light_text: str | None

    @classmethod
    def from_bar(cls, bar: EssenceBar, light_left_min: int | None) -> "EssenceBarOut":
        return cls(
            done_pct=bar.done_pct,
            plan_pct=bar.plan_pct,
            sunset_pct=bar.sunset_pct,
            light_text=None if light_left_min is None else format_duration(light_left_min),
        )
