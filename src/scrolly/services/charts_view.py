from dataclasses import dataclass
from datetime import date

from scrolly.domain.analytics import (
    Bar,
    Metric,
    Point,
    momentum,
    placeholder_momentum,
    placeholder_rhythm,
    rhythm,
    thin,
)
from scrolly.ports import Store
from scrolly.services.golden_core import read_setting


@dataclass(frozen=True)
class Series:
    """Both charts for one metric. A placeholder is a fixed shape, shown under fog."""

    metric: Metric
    momentum: list[Point]
    rhythm: list[Bar]
    placeholder: bool


def build_charts(store: Store, today: date) -> list[Series]:
    """Every metric the user can switch to: Trials and Essence, and Qi with the Golden Core on."""
    trials = store.trials.list_all()
    metrics = [Metric.TRIALS, Metric.ESSENCE]
    if read_setting(store).enabled:
        metrics.append(Metric.QI)
    series = []
    for metric in metrics:
        points = momentum(trials, metric)
        if points:
            series.append(Series(metric, thin(points), rhythm(trials, today, metric), False))
        else:
            series.append(
                Series(metric, placeholder_momentum(today), placeholder_rhythm(today), True)
            )
    return series
