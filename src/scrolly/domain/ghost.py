"""Ghost time: a timer left running while the app was closed or the machine asleep. Pure.

When the app comes back after a long silence with a timer running, the user is asked whether the
silence counts. Whether a silence is long enough is the only rule; what to pause lives in services.
"""

from datetime import datetime, timedelta

GHOST_AFTER = timedelta(hours=1, minutes=30)
# Every request would otherwise write, and a page load makes several at once.
NOTE_EVERY = timedelta(seconds=30)


def is_ghost_gap(last_seen: datetime | None, now: datetime) -> bool:
    """More than an hour and a half since the app last heard from the user."""
    return last_seen is not None and now - last_seen > GHOST_AFTER


def needs_note(last_seen: datetime | None, now: datetime, pending: bool) -> bool:
    """Whether to write "last seen" now: never seen, a question waiting, or 30 s have passed."""
    return last_seen is None or pending or now - last_seen >= NOTE_EVERY
