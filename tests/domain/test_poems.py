from datetime import date, timedelta

from scrolly.domain.poems import ARCHETYPES, poem_for
from scrolly.services.poem_content import load_poems

START = date(2026, 10, 18)


def test_a_day_always_gets_the_same_page() -> None:
    poems = load_poems()
    assert poem_for(START, poems) == poem_for(START, poems)


def test_poems_take_turns_and_every_layout_and_order_comes_round() -> None:
    poems = load_poems()
    picks = [poem_for(START + timedelta(days=n), poems) for n in range(400)]
    assert {p.poem.id for p in picks} == {p.id for p in poems}
    assert {p.archetype for p in picks} == set(ARCHETYPES)
    assert {p.chinese_first for p in picks} == {True, False}


def test_the_next_day_is_a_different_poem() -> None:
    poems = load_poems()
    assert poem_for(START, poems).poem != poem_for(START + timedelta(days=1), poems).poem


def test_the_shipped_poems_are_stand_ins_with_every_field() -> None:
    poems = load_poems()
    assert len(poems) >= 10
    assert len({p.id for p in poems}) == len(poems)
    for poem in poems:
        assert poem.stand_in
        assert len(poem.ideogram) == 1 and poem.pinyin.strip()
        assert all(line.strip() for line in poem.chinese)
        assert poem.english.strip() and poem.reflection.strip()
        assert poem.pairing in {"jade", "gold", "ink"}
