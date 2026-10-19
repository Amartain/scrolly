from pydantic import BaseModel

from scrolly.domain.legend import STATE_SYMBOLS, TYPE_SYMBOLS, Symbol


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
    def build(cls) -> "LegendOut":
        return cls(
            states={s.value: SymbolOut.from_symbol(sym) for s, sym in STATE_SYMBOLS.items()},
            types={t.value: SymbolOut.from_symbol(sym) for t, sym in TYPE_SYMBOLS.items()},
        )
