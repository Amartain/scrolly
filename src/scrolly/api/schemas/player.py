from pydantic import BaseModel

from scrolly.domain.player import AuraColour
from scrolly.services.player import PlayerView


class PlayerOut(BaseModel):
    """The player of the Solo Leveling easter egg. `robe`/`glow`: null is the theme's own;
    `glow_on`: the glow shows always; `rewarded`: the System's reward card was given."""

    is_player: bool
    rewarded: bool
    robe: AuraColour | None
    glow: AuraColour | None
    glow_on: bool
    colours: list[AuraColour]

    @classmethod
    def from_view(cls, view: PlayerView) -> "PlayerOut":
        return cls(
            is_player=view.is_player,
            rewarded=view.rewarded,
            robe=view.robe,
            glow=view.glow,
            glow_on=view.glow_on,
            colours=view.colours,
        )


class AuraIn(BaseModel):
    robe: AuraColour | None
    glow: AuraColour | None
    glow_on: bool
