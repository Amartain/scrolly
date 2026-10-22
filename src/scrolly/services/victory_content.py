"""Reads the day lines of Tribulation Weathered (`scrolly/content/victory.json`)."""

import json
from functools import cache
from importlib.resources import files


@cache
def load_victory_lines() -> list[str]:
    text = (files("scrolly") / "content" / "victory.json").read_text(encoding="utf-8")
    return list(json.loads(text))
