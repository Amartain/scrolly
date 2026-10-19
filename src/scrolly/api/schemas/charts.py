from datetime import date

from pydantic import BaseModel

from scrolly.domain.analytics import Bar, Metric, Point
from scrolly.domain.duration import format_duration
from scrolly.services.charts_view import Series


def _text(metric: Metric, value: int) -> str:
    """A figure as the user reads it: minutes as 1h30m, counts and Qi as plain numbers."""
    return format_duration(value) if metric is Metric.ESSENCE and value > 0 else str(value)


class PointOut(BaseModel):
    day: date
    label: str
    value: int
    value_text: str

    @classmethod
    def from_point(cls, point: Point, metric: Metric) -> "PointOut":
        return cls(
            day=point.day,
            label=f"{point.day:%b} {point.day.day}",
            value=point.value,
            value_text=_text(metric, point.value),
        )


class BarOut(BaseModel):
    day: date
    label: str
    value_text: str
    height_pct: int
    is_rest: bool

    @classmethod
    def from_bar(cls, bar: Bar, metric: Metric) -> "BarOut":
        return cls(
            day=bar.day,
            label=f"{bar.day:%a}",
            value_text=_text(metric, bar.value),
            height_pct=bar.height_pct,
            is_rest=bar.is_rest,
        )


class SeriesOut(BaseModel):
    """Both charts for one metric. `placeholder` data is a fixed shape for the fog."""

    metric: Metric
    momentum: list[PointOut]
    rhythm: list[BarOut]
    placeholder: bool

    @classmethod
    def from_series(cls, series: Series) -> "SeriesOut":
        return cls(
            metric=series.metric,
            momentum=[PointOut.from_point(p, series.metric) for p in series.momentum],
            rhythm=[BarOut.from_bar(b, series.metric) for b in series.rhythm],
            placeholder=series.placeholder,
        )
