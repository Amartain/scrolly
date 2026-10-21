"""Ghost time: the question asked when the app returns after a long silence with a timer running.

Every request notes when the user was last seen. The first one after more than 1.5 hours pauses
whatever was running at the moment they left, and the user is asked: keep all of it, or count only
until they left. Until they answer, the timers stay paused where they left off.
"""

from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.duration import format_duration
from scrolly.domain.ghost import is_ghost_gap
from scrolly.ports import Clock, Store
from scrolly.services.ghost_freeze import Frozen, freeze, thaw

KEY = "ghost"


@dataclass(frozen=True)
class Ghost:
    left_at: datetime
    found_at: datetime
    frozen: Frozen


@dataclass(frozen=True)
class GhostView:
    """What the question says: when the user left, and for how long."""

    left_text: str
    gap_text: str


def _read(store: Store) -> tuple[datetime | None, Ghost | None]:
    saved = store.settings.get(KEY) or {}
    seen = saved.get("last_seen")
    pending = saved.get("pending")
    ghost = None
    if pending:
        left, found = pending["left_at"], pending["found_at"]
        ghost = Ghost(
            datetime.fromisoformat(left),
            datetime.fromisoformat(found),
            Frozen.from_json(pending["frozen"]),
        )
    return (None if seen is None else datetime.fromisoformat(seen)), ghost


def _write(store: Store, seen: datetime, ghost: Ghost | None, now: datetime) -> None:
    pending = None
    if ghost is not None:
        pending = {
            "left_at": ghost.left_at.isoformat(),
            "found_at": ghost.found_at.isoformat(),
            "frozen": ghost.frozen.to_json(),
        }
    store.settings.set(KEY, {"last_seen": seen.isoformat(), "pending": pending}, now)


def build_ghost_view(store: Store) -> GhostView | None:
    _, ghost = _read(store)
    if ghost is None:
        return None
    minutes = int((ghost.found_at - ghost.left_at).total_seconds() // 60)
    return GhostView(ghost.left_at.strftime("%H:%M"), format_duration(minutes))


class GhostService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def watch(self) -> None:
        """Note the user is here. After a long silence, pause what ran when they left."""
        now = self._clock.now()
        seen, ghost = _read(self._store)
        if ghost is None and seen is not None and is_ghost_gap(seen, now):
            frozen = freeze(self._store, seen, now)
            if frozen:
                ghost = Ghost(seen, now, frozen)
        _write(self._store, now, ghost, now)

    def keep(self) -> None:
        """The silence counts: every timer carries on as if it had never stopped."""
        now = self._clock.now()
        _, ghost = _read(self._store)
        if ghost is not None:
            thaw(self._store, ghost.frozen, ghost.left_at, now)
        _write(self._store, now, None, now)

    def cut(self) -> None:
        """Count only until the user left: the timers stay where they were paused."""
        now = self._clock.now()
        _write(self._store, now, None, now)
