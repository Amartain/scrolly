from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from scrolly.api.routes import (
    advisor,
    archives,
    arts,
    dispatch,
    export,
    ghost,
    golden_core,
    header,
    horizon,
    imports,
    knowledge,
    planning,
    planning_timer,
    player,
    scraps,
    seals,
    seclusion,
    sunset,
    trials,
    view,
)
from scrolly.domain.appearance import AppearanceError
from scrolly.domain.archive import ArchiveError
from scrolly.domain.arts import ArtError
from scrolly.domain.day_flow import TrialError
from scrolly.domain.duration import DurationError
from scrolly.domain.header_image import HeaderImageError
from scrolly.domain.horizon import HorizonError
from scrolly.domain.knowledge import KnowledgeError
from scrolly.domain.legend import LegendError
from scrolly.domain.ordering import OrderError
from scrolly.domain.planning import PlanningError
from scrolly.domain.player import PlayerError
from scrolly.domain.qi import QiError
from scrolly.domain.run_clock import RunError
from scrolly.domain.uniqueness import DuplicateTitleError
from scrolly.ports import Clock, StoreFactory
from scrolly.services.ghost import GhostService


def _refuse(status: int) -> Callable[[Request, Exception], JSONResponse]:
    def handler(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=status)

    return handler


def _refuse_title(request: Request, error: Exception) -> JSONResponse:
    """A taken title: the plain message, plus the facts so the interface can word it."""
    assert isinstance(error, DuplicateTitleError)
    body = {"detail": str(error), "refusal": asdict(error.refusal)}
    return JSONResponse(body, status_code=409)


def create_app(
    clock: Clock,
    store_factory: StoreFactory,
    static_dir: Path | None = None,
    data_dir: Path | None = None,
) -> FastAPI:
    """The single composition root: everything the API needs is passed in here."""
    app = FastAPI(title="Scrolly")
    app.state.clock = clock
    app.state.store_factory = store_factory
    # Where the user's files live beside the database: backups made before a restore, the header.
    app.state.data_dir = data_dir
    # Domain errors become HTTP errors only here.
    app.add_exception_handler(PlanningError, _refuse(409))
    app.add_exception_handler(TrialError, _refuse(409))
    app.add_exception_handler(HorizonError, _refuse(409))
    app.add_exception_handler(OrderError, _refuse(409))
    app.add_exception_handler(ArtError, _refuse(409))
    app.add_exception_handler(DuplicateTitleError, _refuse_title)
    app.add_exception_handler(DurationError, _refuse(422))
    app.add_exception_handler(ArchiveError, _refuse(422))
    app.add_exception_handler(LegendError, _refuse(422))
    app.add_exception_handler(AppearanceError, _refuse(422))
    app.add_exception_handler(HeaderImageError, _refuse(422))
    app.add_exception_handler(QiError, _refuse(422))
    app.add_exception_handler(RunError, _refuse(422))
    app.add_exception_handler(KnowledgeError, _refuse(422))
    app.add_exception_handler(PlayerError, _refuse(422))

    @app.middleware("http")
    async def watch_for_ghosts(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Every request notes that the user is here; one after a long silence pauses the timers."""
        path = request.url.path
        if path.startswith("/api/") and path != "/api/health":
            with store_factory() as store:
                GhostService(store, clock).watch()
        return await call_next(request)

    app.include_router(ghost.router)
    app.include_router(view.router)
    app.include_router(golden_core.router)
    app.include_router(sunset.router)
    app.include_router(advisor.router)
    app.include_router(dispatch.router)
    app.include_router(header.router)
    app.include_router(export.router)
    app.include_router(imports.router)
    app.include_router(planning.router)
    app.include_router(planning_timer.router)
    app.include_router(seals.router)
    app.include_router(trials.router)
    app.include_router(seclusion.router)
    app.include_router(scraps.router)
    app.include_router(archives.router)
    app.include_router(horizon.router)
    app.include_router(arts.router)
    app.include_router(knowledge.router)
    app.include_router(player.router)
    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app
