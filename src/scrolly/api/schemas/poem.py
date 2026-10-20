from pydantic import BaseModel

from scrolly.domain.poems import PoemPick


class PoemOut(BaseModel):
    """The sunset poem until it is settled. Layout and language order are chosen in Python."""

    id: str
    ideogram: str
    pinyin: str
    chinese: list[str]
    english: str
    reflection: str
    pairing: str
    archetype: str
    chinese_first: bool
    stand_in: bool

    @classmethod
    def from_pick(cls, pick: PoemPick) -> "PoemOut":
        poem = pick.poem
        return cls(
            id=poem.id,
            ideogram=poem.ideogram,
            pinyin=poem.pinyin,
            chinese=list(poem.chinese),
            english=poem.english,
            reflection=poem.reflection,
            pairing=poem.pairing,
            archetype=pick.archetype,
            chinese_first=pick.chinese_first,
            stand_in=poem.stand_in,
        )
