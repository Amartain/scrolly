"""What the user last chose for Cycles, Flow, sound and the side column, kept in the settings."""

from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.cycles import CyclesPlan, make_plan
from scrolly.domain.run_clock import RATIO_MAX, check_range
from scrolly.ports import Store

CYCLES_KEY = "cycles"
FLOW_KEY = "flow"
SOUND_KEY = "sound"
SCRAPS_KEY = "scraps"
DEFAULT_RATIO = (3, 1)  # the research favours 3:1; 5:1 is hustle culture


@dataclass(frozen=True)
class SoundPrefs:
    volume: int = 60
    muted: bool = False


def load_plan(store: Store) -> CyclesPlan:
    saved = store.settings.get(CYCLES_KEY) or {}
    plan = CyclesPlan()
    return CyclesPlan(
        int(saved.get("focus_min", plan.focus_min)),
        int(saved.get("break_min", plan.break_min)),
        int(saved.get("cycles", plan.cycles)),
    )


def save_plan(store: Store, plan: CyclesPlan, now: datetime) -> None:
    checked = make_plan(plan.focus_min, plan.break_min, plan.cycles)
    saved = {"focus_min": checked.focus_min, "break_min": checked.break_min}
    store.settings.set(CYCLES_KEY, {**saved, "cycles": checked.cycles}, now)


def load_ratio(store: Store) -> tuple[int, int]:
    saved = store.settings.get(FLOW_KEY) or {}
    return int(saved.get("work", DEFAULT_RATIO[0])), int(saved.get("rest", DEFAULT_RATIO[1]))


def save_ratio(store: Store, work: int, rest: int, now: datetime) -> None:
    check_range(work, 1, RATIO_MAX, "The work side of the ratio")
    check_range(rest, 1, RATIO_MAX, "The rest side of the ratio")
    store.settings.set(FLOW_KEY, {"work": work, "rest": rest}, now)


def load_sound(store: Store) -> SoundPrefs:
    saved = store.settings.get(SOUND_KEY) or {}
    return SoundPrefs(int(saved.get("volume", 60)), bool(saved.get("muted", False)))


def save_sound(store: Store, prefs: SoundPrefs, now: datetime) -> None:
    check_range(prefs.volume, 0, 100, "The volume")
    store.settings.set(SOUND_KEY, {"volume": prefs.volume, "muted": prefs.muted}, now)


def load_scraps_hidden(store: Store) -> bool:
    """Whether Bamboo Scraps is folded away in the focus room. Shown until the user hides it."""
    saved = store.settings.get(SCRAPS_KEY) or {}
    return bool(saved.get("hidden", False))


def save_scraps_hidden(store: Store, hidden: bool, now: datetime) -> None:
    store.settings.set(SCRAPS_KEY, {"hidden": hidden}, now)
