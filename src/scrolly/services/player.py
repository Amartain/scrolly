"""The player, kept in the settings: whether the Arise window was accepted, and the chosen aura."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from scrolly.domain import player as rules
from scrolly.domain.player import AuraColour, Player
from scrolly.domain.stats import heavenly_cycles
from scrolly.ports import Store

KEY = "player"


@dataclass(frozen=True)
class PlayerView:
    is_player: bool
    rewarded: bool  # the System's reward card was given
    robe: AuraColour | None
    glow: AuraColour | None
    glow_on: bool
    colours: list[AuraColour]  # what can be chosen, in order


def _colour(saved: Any) -> AuraColour | None:
    return AuraColour(saved) if saved in AuraColour.__members__.values() else None


def read_player(store: Store) -> Player:
    saved = store.settings.get(KEY) or {}
    return Player(
        accepted=bool(saved.get("accepted", False)),
        rewarded=bool(saved.get("rewarded", False)),
        robe=_colour(saved.get("robe")),
        glow=_colour(saved.get("glow")),
        glow_on=bool(saved.get("glow_on", False)),
    )


def write_player(store: Store, player: Player, now: datetime) -> None:
    saved = {
        "accepted": player.accepted,
        "rewarded": player.rewarded,
        "robe": player.robe.value if player.robe else None,
        "glow": player.glow.value if player.glow else None,
        "glow_on": player.glow_on,
    }
    store.settings.set(KEY, saved, now)
    store.commit()


def _cycles(store: Store) -> int:
    return heavenly_cycles(store.days.list_all())


def build_player(store: Store) -> PlayerView:
    player = read_player(store)
    return PlayerView(
        is_player=rules.is_player(player, _cycles(store)),
        rewarded=player.rewarded,
        robe=player.robe,
        glow=player.glow,
        glow_on=player.glow_on,
        colours=list(AuraColour),
    )


class PlayerService:
    def __init__(self, store: Store, now: datetime) -> None:
        self._store = store
        self._now = now

    def accept(self) -> None:
        """[ Yes ] on the Arise window."""
        write_player(self._store, rules.accept(read_player(self._store)), self._now)

    def choose_aura(self, robe: AuraColour | None, glow: AuraColour | None, glow_on: bool) -> None:
        player = read_player(self._store)
        chosen = rules.choose_aura(player, _cycles(self._store), robe, glow, glow_on)
        write_player(self._store, chosen, self._now)
