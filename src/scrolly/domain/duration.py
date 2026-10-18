import re

_HOURS_MINUTES = re.compile(r"(?:(\d+(?:\.\d+)?)h)?(?:(\d+)m)?")


class DurationError(ValueError):
    pass


def parse_duration(text: str) -> int | None:
    """Minutes from "45m", "1h", "1.5h", "1h15m", "90" (minutes) or blank (None)."""
    cleaned = "".join(text.split()).lower()
    if not cleaned:
        return None
    if cleaned.isdigit():
        return int(cleaned)
    match = _HOURS_MINUTES.fullmatch(cleaned)
    if match is None or not any(match.groups()):
        raise DurationError(f"Not a duration: {text!r}")
    hours, minutes = match.groups()
    return round(float(hours or 0) * 60) + int(minutes or 0)


def format_duration(minutes: int) -> str:
    """The inverse of parse_duration: "45m", "2h", "1h15m"."""
    hours, rest = divmod(minutes, 60)
    if hours == 0:
        return f"{rest}m"
    return f"{hours}h" if rest == 0 else f"{hours}h{rest}m"
