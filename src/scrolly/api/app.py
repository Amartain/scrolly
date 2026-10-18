from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from scrolly.api.routes import imports, view
from scrolly.ports import Clock, StoreFactory


def create_app(
    clock: Clock, store_factory: StoreFactory, static_dir: Path | None = None
) -> FastAPI:
    """The single composition root: everything the API needs is passed in here."""
    app = FastAPI(title="Scrolly")
    app.state.clock = clock
    app.state.store_factory = store_factory
    app.include_router(view.router)
    app.include_router(imports.router)
    if static_dir is not None and static_dir.is_dir():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app
