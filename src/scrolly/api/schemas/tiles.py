from pydantic import BaseModel

from scrolly.domain.day_tiles import Tile, TileState


class TileOut(BaseModel):
    """One trial on the dashboard's Essence or Qi row: its share of the row, and its numbers."""

    title: str
    state: TileState
    share_pct: float
    taken: str | None
    planned: str | None

    @classmethod
    def from_tile(cls, tile: Tile) -> "TileOut":
        return cls(
            title=tile.title,
            state=tile.state,
            share_pct=round(tile.share_pct, 2),
            taken=tile.taken,
            planned=tile.planned,
        )
