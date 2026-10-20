from pydantic import BaseModel

from scrolly.domain.legend import Legend, Symbol


class SymbolOut(BaseModel):
    emoji: str
    shortcode: str
    label: str

    @classmethod
    def from_symbol(cls, symbol: Symbol) -> "SymbolOut":
        return cls(emoji=symbol.emoji, shortcode=symbol.shortcode, label=symbol.label)


class LegendOut(BaseModel):
    """Keyed by trial state (`immediate`, `done`, ...) and by trial type (`mandate`, ...)."""

    states: dict[str, SymbolOut]
    types: dict[str, SymbolOut]

    @classmethod
    def build(cls, legend: Legend) -> "LegendOut":
        return cls(
            states={s.value: SymbolOut.from_symbol(sym) for s, sym in legend.states.items()},
            types={t.value: SymbolOut.from_symbol(sym) for t, sym in legend.types.items()},
        )
