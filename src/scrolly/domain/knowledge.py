"""Knowledge of the Dao: the tour of Scrolly, played like a game (owner, 2026-10-23). Pure, no IO.

Steps are the main walkthrough, in order: a card points at the feature and the step is done by doing
it. Finds are the smaller things, learned the first time they are tried. Both fill one bar. Learning
never goes back: walking the path again shows the step cards again but unlearns nothing (nothing
punitive, no decreasing metric). When everything is learned, the cultivator is enlightened, once.
"""

from dataclasses import dataclass, field, replace
from enum import StrEnum


class Kind(StrEnum):
    STEP = "step"
    FIND = "find"


@dataclass(frozen=True)
class Lesson:
    key: str
    kind: Kind


def _steps(*keys: str) -> tuple[Lesson, ...]:
    return tuple(Lesson(key, Kind.STEP) for key in keys)


def _finds(*keys: str) -> tuple[Lesson, ...]:
    return tuple(Lesson(key, Kind.FIND) for key in keys)


# The owner approved these lists (phase 12). Steps keep this order: Phase 1, Phase 2, the dashboard.
CATALOGUE: tuple[Lesson, ...] = (
    *_finds("open", "cultivate"),
    *_steps("dump", "orbs", "proceed", "estimate", "mandate", "seal"),
    *_steps("timer", "conquer", "seclusion", "screen-two", "horizon", "arts"),
    *_finds("planning-clock", "reorder", "sunset", "golden-core"),
    *_finds("scribe", "promote", "postpone", "abandon", "resummon", "revive", "correct-time"),
    *_finds("charts", "cycles", "river-flow", "parallel", "scraps", "step-out"),
    *_finds("dispatch", "archives", "scraps-page", "guidance", "qi-card", "settings"),
)
KEYS = frozenset(lesson.key for lesson in CATALOGUE)


class KnowledgeError(ValueError):
    """Not a lesson of the tour. The message is shown to the user."""


@dataclass(frozen=True)
class Knowledge:
    learned: frozenset[str] = field(default_factory=frozenset)
    walked: frozenset[str] = field(default_factory=frozenset)  # step cards done on this walk
    tour: bool = True  # cards are shown; learning goes on either way
    bar_hidden: bool = False  # the bar shows only for a moment when it moves
    enlightened: bool = False  # the ceremony was seen


def learn(knowledge: Knowledge, key: str) -> Knowledge:
    """`key` was tried. Learning it again changes nothing."""
    if key not in KEYS:
        raise KnowledgeError(f"There is no lesson called {key}")
    return replace(knowledge, learned=knowledge.learned | {key}, walked=knowledge.walked | {key})


def pass_step(knowledge: Knowledge, key: str) -> Knowledge:
    """Got it, on a step card: the card goes, nothing is learned. Doing the thing later still
    fills the bar."""
    if key not in KEYS:
        raise KnowledgeError(f"There is no lesson called {key}")
    return replace(knowledge, walked=knowledge.walked | {key})


def pending_steps(knowledge: Knowledge) -> list[str]:
    """The step cards still to show, in order. None while the tour is off."""
    if not knowledge.tour:
        return []
    steps = (lesson.key for lesson in CATALOGUE if lesson.kind is Kind.STEP)
    return [key for key in steps if key not in knowledge.walked]


def walk_again(knowledge: Knowledge) -> Knowledge:
    """Show the step cards again. What was learned stays learned."""
    return replace(knowledge, walked=frozenset(), tour=True)


def complete(knowledge: Knowledge) -> bool:
    return knowledge.learned >= KEYS
