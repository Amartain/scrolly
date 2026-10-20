"""The sunset poem: which one, in which layout, in which order. Pure."""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

ARCHETYPES = (
    "classical-imperial-scroll",
    "translation-hero",
    "mountain-hermit-asymmetry",
    "retro-scholar-tablet",
    "split-column-pavilion",
    "zen-monograph",
    "golden-pavilion-seal",
)


@dataclass(frozen=True)
class Poem:
    id: str
    ideogram: str
    pinyin: str  # the title, in pinyin
    chinese: tuple[str, str]  # the couplet
    english: str
    reflection: str
    pairing: str  # which token pair paints it: jade, gold or ink
    # A placeholder written for this app. Real, sourced poems replace them in step 10.
    stand_in: bool = False


@dataclass(frozen=True)
class PoemPick:
    poem: Poem
    archetype: str
    chinese_first: bool


def poem_for(day: date, poems: Sequence[Poem]) -> PoemPick:
    """The poem for a logical day. Poems take turns; the layout and the order of the two languages
    vary from day to day, and a reload on the same day shows the same page."""
    ordinal = day.toordinal()
    chance = random.Random(ordinal)
    return PoemPick(
        poem=poems[ordinal % len(poems)],
        archetype=chance.choice(ARCHETYPES),
        chinese_first=chance.random() < 0.5,
    )
