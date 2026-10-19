"""The old Flask app's backup: an object of five lists, or one bare list."""

import json
from datetime import UTC, date, datetime
from typing import Any

from scrolly.domain.art_match import kind_of_origin
from scrolly.domain.merge import ImportBatch
from scrolly.domain.models import (
    Art,
    ArtKind,
    HorizonItem,
    OriginType,
    Trial,
    TrialState,
)
from scrolly.io.errors import ImportFormatError
from scrolly.io.ids import stable_id

_STATUS = {
    "Done": TrialState.DONE,
    "Next": TrialState.IMMEDIATE,
    "Remaining": TrialState.REMAINING,
    "Postponed": TrialState.POSTPONED,
    "Cancelled": TrialState.LOST,
}
_SECTIONS = ("current", "history", "future", "rituals", "restorations")
_FILE_SECTIONS = {
    "current_day": "current",
    "history": "history",
    "future_trials": "future",
    "rituals": "rituals",
    "restorations": "restorations",
}


def _minutes(value: Any) -> int | None:
    """Minutes, where 0 or missing means "no estimate"."""
    return (int(value) or None) if value else None


def _origin(raw: dict[str, Any]) -> OriginType:
    if raw.get("is_ritual"):
        return OriginType.FOUNDATIONAL_ART
    if raw.get("is_restorative"):
        return OriginType.RESTORATIVE_ART
    return OriginType.BRAIN_DUMP


def _trial(raw: dict[str, Any], position: int) -> Trial:
    state = _STATUS[raw["status"]]
    done = state is TrialState.DONE
    spent = int(raw.get("spent_time_secs") or 0)
    actual = _minutes(raw.get("actual_time_mins")) or _minutes(round(spent / 60))
    millis = int(raw.get("completed_at") or 0)
    return Trial(
        id=stable_id("prototype", raw["id"]),
        logical_day=date.fromisoformat(raw["logical_date"]),
        title=str(raw["description"]).strip(),
        state=state,
        is_mandate=bool(raw.get("mandate")),
        origin_type=_origin(raw),
        art_kind=kind_of_origin(_origin(raw)),
        position=position,
        essence_expected_min=_minutes(raw.get("expected_time_mins")),
        essence_actual_min=actual if done else None,
        completed_at=datetime.fromtimestamp(millis / 1000, UTC) if done and millis > 0 else None,
        timer_accumulated_s=spent,
    )


def _horizon_item(raw: dict[str, Any]) -> HorizonItem:
    return HorizonItem(
        id=stable_id("prototype", raw["id"]),
        title=str(raw["description"]).strip(),
        is_mandate=bool(raw.get("mandate")),
        essence_expected_min=_minutes(raw.get("expected_time_mins")),
        origin_type=_origin(raw),
        art_kind=kind_of_origin(_origin(raw)),
    )


def _art(raw: dict[str, Any], kind: ArtKind) -> Art:
    return Art(
        id=stable_id("prototype", raw["id"]),
        kind=kind,
        title=str(raw["description"]).strip(),
        essence_expected_min=_minutes(raw.get("expected_time_mins")),
    )


def _bare_list_section(items: list[Any], name: str) -> str:
    """Which section a lone list is: by file name, else by the Art id prefix, else history."""
    if name in _FILE_SECTIONS:
        return _FILE_SECTIONS[name]
    first = str(items[0].get("id", "")) if items and isinstance(items[0], dict) else ""
    if first.startswith("rs_"):
        return "restorations"
    return "rituals" if first.startswith("r_") else "history"


def _sections(data: Any, name: str) -> dict[str, list[dict[str, Any]]]:
    if isinstance(data, dict):
        found = {key: data[key] for key in _SECTIONS if isinstance(data.get(key), list)}
        if not found:
            raise ImportFormatError("This JSON has none of: " + ", ".join(_SECTIONS))
        return found
    if not isinstance(data, list):
        raise ImportFormatError("Expected a JSON object or a list of trials")
    return {_bare_list_section(data, name): data}


def parse_prototype_json(text: str, name: str = "") -> ImportBatch:
    try:
        sections = _sections(json.loads(text), name)
        trials = [
            _trial(raw, position)
            for key in ("current", "history")
            for position, raw in enumerate(sections.get(key, []))
        ]
        horizon = [_horizon_item(raw) for raw in sections.get("future", [])]
        arts = [_art(raw, ArtKind.FOUNDATIONAL) for raw in sections.get("rituals", [])]
        arts += [_art(raw, ArtKind.RESTORATIVE) for raw in sections.get("restorations", [])]
    except json.JSONDecodeError as error:
        raise ImportFormatError("This file is not valid JSON") from error
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ImportFormatError(f"A row in this file could not be read ({error!r})") from error
    return ImportBatch(trials=trials, horizon=horizon, arts=arts)
