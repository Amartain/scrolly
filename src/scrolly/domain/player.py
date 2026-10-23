"""The player (owner, 2026-10-23): the Solo Leveling easter egg goes on after the Arise window.

Whoever answers its [ Yes ] becomes a player, for good, and the System rewards the accepted quest
with blue cultivation robes and a blue glow. Reaching Day 100 makes a player too (that window was
seen, and Heavenly Cycles never fall), so those who got there before this rule are not left out.
A player picks the robe and the glow from the theme colours, and can switch the glow off.
"""

from dataclasses import dataclass, replace
from enum import StrEnum

from scrolly.domain.secret_seals import ARISE_DAY


class AuraColour(StrEnum):
    """The colours a player can wear: one from each theme, and the System's own blue."""

    SYSTEM_BLUE = "system-blue"
    GOLD = "gold"
    JADE = "jade"
    TEAL = "teal"
    CRIMSON = "crimson"
    VIOLET = "violet"
    CREAM = "cream"


REWARD = AuraColour.SYSTEM_BLUE


class PlayerError(ValueError):
    """A choice only a player can make. The message is shown to the user."""


@dataclass(frozen=True)
class Player:
    accepted: bool = False  # answered [ Yes ] to the Arise window
    rewarded: bool = False  # the System's reward card was given
    robe: AuraColour | None = None  # None: the theme's own robe (gold once enlightened)
    glow: AuraColour | None = None  # None: the theme's own aura (gold)
    glow_on: bool = False  # the glow shows always, not only at golden hour and dusk


def is_player(player: Player, heavenly_cycles: int) -> bool:
    return player.accepted or heavenly_cycles >= ARISE_DAY


def accept(player: Player) -> Player:
    """[ Yes ]. The first time, the reward: blue robes and a blue glow, shining. Later answers keep
    whatever the player has chosen since."""
    if player.rewarded:
        return replace(player, accepted=True)
    return Player(accepted=True, rewarded=True, robe=REWARD, glow=REWARD, glow_on=True)


def choose_aura(
    player: Player,
    heavenly_cycles: int,
    robe: AuraColour | None,
    glow: AuraColour | None,
    glow_on: bool,
) -> Player:
    """The player's own robe and glow. Not a player yet: refused."""
    if not is_player(player, heavenly_cycles):
        raise PlayerError("Only a player can choose an aura")
    return replace(player, robe=robe, glow=glow, glow_on=glow_on)
