"""Knowledge of the Dao, kept in the settings: what was learned, the walk of the step cards, and the
user's choices (the tour on or off, the bar shown or hidden)."""

from dataclasses import dataclass, replace
from datetime import datetime

from scrolly.domain import knowledge as rules
from scrolly.domain.knowledge import Knowledge
from scrolly.ports import Store

KEY = "knowledge"


@dataclass(frozen=True)
class KnowledgeView:
    learned: list[str]
    count: int
    total: int
    pending_steps: list[str]  # the step cards still to show, in order
    tour: bool
    bar_hidden: bool
    complete: bool  # everything is learned
    enlightened: bool  # and the ceremony was seen


def read_knowledge(store: Store) -> Knowledge:
    saved = store.settings.get(KEY) or {}
    known = rules.KEYS  # a lesson since retired is dropped, so the bar never runs past full
    return Knowledge(
        learned=frozenset(saved.get("learned", [])) & known,
        walked=frozenset(saved.get("walked", [])) & known,
        tour=bool(saved.get("tour", True)),
        bar_hidden=bool(saved.get("bar_hidden", False)),
        enlightened=bool(saved.get("enlightened", False)),
    )


def write_knowledge(store: Store, knowledge: Knowledge, now: datetime) -> None:
    saved = {
        "learned": sorted(knowledge.learned),
        "walked": sorted(knowledge.walked),
        "tour": knowledge.tour,
        "bar_hidden": knowledge.bar_hidden,
        "enlightened": knowledge.enlightened,
    }
    store.settings.set(KEY, saved, now)


def build_knowledge(store: Store) -> KnowledgeView:
    known = read_knowledge(store)
    return KnowledgeView(
        learned=sorted(known.learned),
        count=len(known.learned),
        total=len(rules.KEYS),
        pending_steps=rules.pending_steps(known),
        tour=known.tour,
        bar_hidden=known.bar_hidden,
        complete=rules.complete(known),
        enlightened=known.enlightened,
    )


class KnowledgeService:
    def __init__(self, store: Store, now: datetime) -> None:
        self._store = store
        self._now = now

    def _put(self, knowledge: Knowledge) -> None:
        write_knowledge(self._store, knowledge, self._now)

    def learn(self, key: str) -> None:
        known = read_knowledge(self._store)
        learned = rules.learn(known, key)
        if learned != known:
            self._put(learned)

    def pass_step(self, key: str) -> None:
        self._put(rules.pass_step(read_knowledge(self._store), key))

    def choose(self, tour: bool | None = None, bar_hidden: bool | None = None) -> None:
        """Only what is given changes."""
        known = read_knowledge(self._store)
        tour = known.tour if tour is None else tour
        hidden = known.bar_hidden if bar_hidden is None else bar_hidden
        self._put(replace(known, tour=tour, bar_hidden=hidden))

    def walk_again(self) -> None:
        self._put(rules.walk_again(read_knowledge(self._store)))

    def enlightened(self) -> None:
        """The ceremony was seen. Only once everything is learned."""
        known = read_knowledge(self._store)
        if not rules.complete(known):
            raise rules.KnowledgeError("The path is not walked yet")
        self._put(replace(known, enlightened=True))
