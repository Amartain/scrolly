import pytest

from scrolly.domain.player import (
    AuraColour,
    Player,
    PlayerError,
    accept,
    choose_aura,
    is_player,
)


def test_nobody_is_a_player_before_the_arise_window() -> None:
    assert not is_player(Player(), heavenly_cycles=99)


def test_answering_yes_makes_a_player_for_good() -> None:
    assert is_player(accept(Player()), heavenly_cycles=0)


def test_day_100_makes_a_player_even_without_an_answer_on_record() -> None:
    assert is_player(Player(), heavenly_cycles=100)


def test_the_first_yes_brings_the_reward_blue_robes_and_a_shining_blue_glow() -> None:
    rewarded = accept(Player())
    assert rewarded.rewarded
    assert rewarded.robe is AuraColour.SYSTEM_BLUE
    assert rewarded.glow is AuraColour.SYSTEM_BLUE
    assert rewarded.glow_on


def test_a_later_yes_keeps_the_aura_the_player_chose() -> None:
    chosen = choose_aura(accept(Player()), 0, AuraColour.JADE, None, glow_on=False)
    again = accept(chosen)
    assert (again.robe, again.glow, again.glow_on) == (AuraColour.JADE, None, False)


def test_a_player_chooses_robe_and_glow_or_the_themes_own() -> None:
    chosen = choose_aura(Player(), 100, AuraColour.CRIMSON, AuraColour.GOLD, glow_on=True)
    assert (chosen.robe, chosen.glow, chosen.glow_on) == (AuraColour.CRIMSON, AuraColour.GOLD, True)
    plain = choose_aura(chosen, 100, None, None, glow_on=False)
    assert (plain.robe, plain.glow) == (None, None)


def test_only_a_player_can_choose_an_aura() -> None:
    with pytest.raises(PlayerError):
        choose_aura(Player(), 99, AuraColour.GOLD, None, glow_on=True)
