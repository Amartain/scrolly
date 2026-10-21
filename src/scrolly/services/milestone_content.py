"""Reads the milestone table and the quotes that ship with the app (`scrolly/content/*.json`)."""

import json
from functools import cache
from importlib.resources import files
from typing import Any

from scrolly.domain.milestones import Milestone, MilestoneRow, Quote, milestone_for


def _read(name: str) -> list[dict[str, Any]]:
    text = (files("scrolly") / "content" / name).read_text(encoding="utf-8")
    data: list[dict[str, Any]] = json.loads(text)
    return data


def _quote(raw: dict[str, Any] | None) -> Quote | None:
    if raw is None:
        return None
    return Quote(raw["text"], raw.get("attribution"), bool(raw.get("stand_in", False)))


@cache
def load_quotes() -> list[Quote]:
    return [q for raw in _read("quotes.json") if (q := _quote(raw)) is not None]


@cache
def load_milestones() -> list[MilestoneRow]:
    return [
        MilestoneRow(
            raw["day"], _quote(raw.get("quote")), raw.get("banner"), raw.get("style", "plain")
        )
        for raw in _read("milestones.json")
    ]


def milestone_after(cycles: int) -> Milestone:
    """The milestone for the day just sealed, from the content that ships with the app."""
    return milestone_for(cycles, load_milestones(), load_quotes())
