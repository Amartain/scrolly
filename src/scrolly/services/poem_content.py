"""Reads the sunset poems that ship with the app (`scrolly/content/poems.json`)."""

import json
from functools import cache
from importlib.resources import files

from scrolly.domain.poems import Poem


@cache
def load_poems() -> list[Poem]:
    text = (files("scrolly") / "content" / "poems.json").read_text(encoding="utf-8")
    return [
        Poem(
            id=raw["id"],
            ideogram=raw["ideogram"],
            pinyin=raw["pinyin"],
            chinese=(raw["chinese"][0], raw["chinese"][1]),
            english=raw["english"],
            reflection=raw["reflection"],
            pairing=raw["pairing"],
            stand_in=bool(raw.get("stand_in", False)),
        )
        for raw in json.loads(text)
    ]
