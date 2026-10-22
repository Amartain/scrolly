from typing import Annotated

from fastapi import APIRouter, Depends

from scrolly.api.deps import get_clock, get_store
from scrolly.api.schemas.view import (
    AppearanceIn,
    HealthOut,
    ReadingFontIn,
    SoundIn,
    ViewOut,
)
from scrolly.ports import Clock, Store
from scrolly.services.appearance import AppearanceService
from scrolly.services.seclusion_prefs import SoundPrefs, load_sound, save_sound
from scrolly.services.view import build_view

router = APIRouter(prefix="/api")

StoreDep = Annotated[Store, Depends(get_store)]
ClockDep = Annotated[Clock, Depends(get_clock)]


@router.get("/health")
def health() -> HealthOut:
    return HealthOut()


@router.get("/view")
def view(store: StoreDep, clock: ClockDep) -> ViewOut:
    return ViewOut.from_data(build_view(store, clock))


@router.put("/appearance")
def choose_appearance(body: AppearanceIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    AppearanceService(store, clock).choose(body.theme, body.day_variant)
    return ViewOut.from_data(build_view(store, clock))


@router.put("/sound")
def choose_sound(body: SoundIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    saved = load_sound(store)
    volume = saved.volume if body.volume is None else body.volume
    muted = saved.muted if body.muted is None else body.muted
    save_sound(store, SoundPrefs(volume, muted), clock.now())
    return ViewOut.from_data(build_view(store, clock))


@router.put("/reading-font")
def choose_reading_font(body: ReadingFontIn, store: StoreDep, clock: ClockDep) -> ViewOut:
    AppearanceService(store, clock).choose_reading_font(body.font)
    return ViewOut.from_data(build_view(store, clock))
