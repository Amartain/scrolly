from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from scrolly.api.routes import golden_core, imports, planning, view
from scrolly.domain.duration import DurationError
from scrolly.domain.planning import PlanningError
from scrolly.domain.qi import QiError
from scrolly.ports import Clock, StoreFactory


def _refuse(status: int) -> Callable[[Request, Exception], JSONResponse]:
    def handler(request: Request, error: Exception) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=status)

    return handler


def create_app(
    clock: Clock, store_factory: StoreFactory, static_dir: Path | None = None
) -> FastAPI:
    """The single composition root: everything the API needs is passed in here."""
    app = FastAPI(title="Scrolly")
    app.state.clock = clock
    app.state.store_factory = store_factory
    # Domain errors become HTTP errors only here.
    app.add_exception_handler(PlanningError, _refuse(409))
    app.add_exception_handler(DurationError, _refuse(422))
    app.add_exception_handler(QiError, _refuse(422))
    app.include_router(view.router)
    app.include_router(golden_core.router)
    app.include_router(imports.router)
    app.include_router(planning.router)
    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app
