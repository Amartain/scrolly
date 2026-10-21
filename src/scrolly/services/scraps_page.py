"""The Bamboo Scraps page: every kept scrap, newest first, as it is shown and as Markdown."""

from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.duration import format_duration
from scrolly.domain.logical_day import logical_day
from scrolly.domain.scraps import Scrap, scrap_lanes, visit_seconds
from scrolly.ports import Store

REMOVED = "A trial since removed"


@dataclass(frozen=True)
class SpanView:
    start_pct: float
    width_pct: float


@dataclass(frozen=True)
class LaneView:
    title: str
    spans: list[SpanView]


@dataclass(frozen=True)
class ScrapPage:
    id: str
    day_text: str
    time_text: str
    length_text: str
    text: str
    lanes: list[LaneView]


def _percent(part: int, whole: int) -> float:
    return round(100 * part / whole, 2) if whole else 0.0


def _page(scrap: Scrap, store: Store, titles: dict[str, str], now: datetime) -> ScrapPage:
    assert scrap.closed_at is not None
    opened = scrap.opened_at.astimezone(now.tzinfo)
    closed = scrap.closed_at.astimezone(now.tzinfo)
    day = logical_day(opened)
    total = visit_seconds(scrap)
    segments = {i: store.segments.list_for_trial(i) for i in scrap.trial_ids}
    lanes = [
        LaneView(
            titles.get(lane.trial_id, REMOVED),
            [SpanView(_percent(a, total), _percent(b - a, total)) for a, b in lane.spans],
        )
        for lane in scrap_lanes(scrap, segments)
    ]
    return ScrapPage(
        scrap.id,
        f"{day:%A}, {day.day} {day:%B %Y}",
        f"{opened:%H:%M}\N{EN DASH}{closed:%H:%M}",
        format_duration(total // 60),
        scrap.text,
        lanes,
    )


def build_scrap_pages(store: Store, now: datetime) -> list[ScrapPage]:
    """Kept scraps whose visit has ended, newest first."""
    titles = {t.id: t.title for t in store.trials.list_all()}
    closed = [s for s in store.scraps.list_all() if not s.is_open]
    return [_page(s, store, titles, now) for s in reversed(closed)]


def scraps_markdown(pages: list[ScrapPage]) -> str:
    """All scraps as one Markdown file, newest first: a heading, the trials worked, the text."""
    scraps = []
    for page in pages:
        trials = " · ".join(lane.title for lane in page.lanes)
        lines = [f"## {page.day_text} · {page.time_text}"]
        if trials:
            lines.append(f"Trials: {trials}")
        scraps.append("\n\n".join(["\n".join(lines), page.text.strip("\n")]))
    return "# Bamboo Scraps\n\n" + "\n\n---\n\n".join(scraps) + "\n"
