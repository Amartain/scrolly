from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.scraps import ScrapIn, ScrapPageOut, ScrapTextOut
from scrolly.ports import Clock, Store
from scrolly.services.scraps import ScrapService
from scrolly.services.scraps_page import build_scrap_pages, scraps_markdown

router = APIRouter(prefix="/api/scraps")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.get("")
def pages(store: StoreDep, clock: ClockDep) -> list[ScrapPageOut]:
    """Every kept scrap, newest first."""
    return [ScrapPageOut.from_page(p) for p in build_scrap_pages(store, clock.now())]


@router.get("/export.md")
def export_markdown(store: StoreDep, clock: ClockDep) -> Response:
    """All scraps as one Markdown file, ready for a notes app."""
    now = clock.now()
    text = scraps_markdown(build_scrap_pages(store, now))
    return Response(
        text,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="bamboo-scraps-{now:%Y-%m-%d}.md"'},
    )


@router.get("/current")
def current(store: StoreDep, clock: ClockDep) -> ScrapTextOut:
    """What is written on the scrap of this visit so far."""
    return ScrapTextOut(text=ScrapService(store, clock).text())


@router.put("/current")
def write(body: ScrapIn, store: StoreDep, clock: ClockDep) -> ScrapTextOut:
    """Save what is written, as it is written. Only inside Seclusion."""
    scraps = ScrapService(store, clock)
    scraps.write(body.text)
    return ScrapTextOut(text=scraps.text())
