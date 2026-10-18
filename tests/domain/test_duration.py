import pytest
from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.duration import DurationError, format_duration, parse_duration


@pytest.mark.parametrize(
    ("text", "minutes"),
    [
        ("45m", 45),
        ("1h", 60),
        ("1.5h", 90),
        ("1h15m", 75),
        ("90", 90),
        (" 1H 15M ", 75),
        ("0", 0),
        ("", None),
        ("   ", None),
    ],
)
def test_parse_accepts_every_documented_form(text: str, minutes: int | None) -> None:
    assert parse_duration(text) == minutes


@pytest.mark.parametrize("text", ["abc", "m", "1x", "-5", "1h 2", "1.5"])
def test_parse_rejects_nonsense(text: str) -> None:
    with pytest.raises(DurationError):
        parse_duration(text)


@pytest.mark.parametrize(
    ("minutes", "text"), [(0, "0m"), (45, "45m"), (60, "1h"), (75, "1h15m"), (120, "2h")]
)
def test_format(minutes: int, text: str) -> None:
    assert format_duration(minutes) == text


@given(st.integers(min_value=0, max_value=100_000))
def test_format_then_parse_round_trips(minutes: int) -> None:
    assert parse_duration(format_duration(minutes)) == minutes
