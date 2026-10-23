import pytest

from scrolly.domain.knowledge import (
    CATALOGUE,
    KEYS,
    Kind,
    Knowledge,
    KnowledgeError,
    complete,
    learn,
    pass_step,
    pending_steps,
    walk_again,
)

STEPS = [lesson.key for lesson in CATALOGUE if lesson.kind is Kind.STEP]


def test_the_walkthrough_is_the_twelve_steps_the_owner_approved_in_order() -> None:
    assert STEPS == [
        "dump",
        "orbs",
        "proceed",
        "estimate",
        "mandate",
        "seal",
        "timer",
        "conquer",
        "seclusion",
        "screen-two",
        "horizon",
        "arts",
    ]
    assert len(KEYS) == len(CATALOGUE)  # no lesson twice


def test_a_step_done_leaves_the_walk_and_fills_the_bar() -> None:
    known = learn(Knowledge(), "dump")
    assert "dump" in known.learned
    assert pending_steps(known)[0] == "orbs"


def test_learning_twice_changes_nothing_and_an_unknown_lesson_is_refused() -> None:
    once = learn(Knowledge(), "charts")
    assert learn(once, "charts") == once
    with pytest.raises(KnowledgeError):
        learn(once, "flying")


def test_got_it_sets_a_step_aside_without_learning_it() -> None:
    passed = pass_step(Knowledge(), "dump")
    assert "dump" not in passed.learned
    assert pending_steps(passed)[0] == "orbs"
    assert "dump" in learn(passed, "dump").learned


def test_with_the_tour_off_no_card_shows_but_learning_goes_on() -> None:
    off = Knowledge(tour=False)
    assert pending_steps(off) == []
    assert "seal" in learn(off, "seal").learned


def test_walking_again_shows_the_cards_and_unlearns_nothing() -> None:
    known = learn(learn(Knowledge(tour=False), "dump"), "orbs")
    again = walk_again(known)
    assert again.learned == known.learned
    assert pending_steps(again) == STEPS


def test_everything_learned_is_complete() -> None:
    known = Knowledge()
    for key in KEYS:
        assert not complete(known)
        known = learn(known, key)
    assert complete(known)
