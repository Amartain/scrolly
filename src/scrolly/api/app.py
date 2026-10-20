from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from scrolly.api.routes import (
    advisor,
    arts,
    dispatch,
    export,
    golden_core,
    horizon,
    imports,
    planning,
    sunset,
    trials,
    view,
)
from scrolly.domain.archive import ArchiveError
from scrolly.domain.arts import ArtError
from scrolly.domain.day_flow import TrialError
from scrolly.domain.duration import DurationError
from scrolly.domain.horizon import HorizonError
from scrolly.domain.legend import LegendError
from scrolly.domain.ordering import OrderError
from scrolly.domain.planning import PlanningError
from scrolly.domain.qi import QiError
from scrolly.domain.uniqueness import DuplicateTitleError
from scrolly.ports import Clock, StoreFactory


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
    backup_dir: Path | None = None,
) -> FastAPI:
    """The single composition root: everything the API needs is passed in here."""
    app = FastAPI(title="Scrolly")
    app.state.clock = clock
    app.state.store_factory = store_factory
    app.state.backup_dir = backup_dir
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
    app.add_exception_handler(QiError, _refuse(422))
    app.include_router(view.router)
    app.include_router(golden_core.router)
    app.include_router(sunset.router)
    app.include_router(advisor.router)
    app.include_router(dispatch.router)
    app.include_router(export.router)
    app.include_router(imports.router)
    app.include_router(planning.router)
    app.include_router(trials.router)
    app.include_router(horizon.router)
    app.include_router(arts.router)
    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app
