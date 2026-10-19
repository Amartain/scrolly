import pytest
from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.duration import DurationError, format_duration, parse_duration


@pytest.mark.parametrize(
    ("text", "minutes"),
    [
        ("45m", 45),
        ("1m", 1),
        ("90m", 90),
        ("2h", 120),
        ("1h15m", 75),
        ("1h0m", 60),
        (" 1H 15M ", 75),
        ("16h", 960),
        ("15h59m", 959),
        ("", None),
        ("   ", None),
    ],
)
def test_parse_accepts_the_three_forms(text: str, minutes: int | None) -> None:
    assert parse_duration(text) == minutes


@pytest.mark.parametrize(
    "text",
    [
        "90",
        "0",
        "1.5h",
        "1.5",
        "0m",
        "0h",
        "17h",
        "5000h",
        "1h75m",
        "16h1m",
        "abc",
        "m",
        "1x",
        "-5",
        "\u00b2",
        "\u0661h",
    ],
)
def test_parse_rejects_everything_else_with_the_hint(text: str) -> None:
    with pytest.raises(DurationError, match="Use 45m, 2h or 1h30m"):
        parse_duration(text)


@pytest.mark.parametrize(
    ("minutes", "text"), [(1, "1m"), (45, "45m"), (60, "1h"), (75, "1h15m"), (120, "2h")]
)
def test_format(minutes: int, text: str) -> None:
    assert format_duration(minutes) == text


@given(st.integers(min_value=1, max_value=960))
def test_format_then_parse_round_trips(minutes: int) -> None:
    assert parse_duration(format_duration(minutes)) == minutes


@given(st.text())
def test_any_text_gives_minutes_or_a_duration_error(text: str) -> None:
    try:
        result = parse_duration(text)
    except DurationError:
        return
    assert result is None or 1 <= result <= 960
