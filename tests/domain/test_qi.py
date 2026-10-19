from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.models import ArtKind, TrialState
from scrolly.domain.qi import (
    GaugeFill,
    QiDay,
    QiError,
    choose_start,
    gauge_fill,
    next_start,
    outlook,
    parse_qi,
    planned,
    redline,
    spent,
    strain_for,
)
from tests.factories import make_trial

TODAY = date(2026, 10, 18)


def day(back: int, start: int, used: int) -> QiDay:
    return QiDay(TODAY - timedelta(days=back), start, used)


@pytest.mark.parametrize(
    ("used", "expected"),
    [
        (0, 0), (100, 0), (101, 1), (115, 15), (130, 30), (131, 34), (140, 59), (150, 74),
        (160, 82), (170, 86), (180, 88), (192, 89), (199, 89), (200, 90), (260, 90),
    ],
)  # fmt: skip
def test_strain_curve_at_a_start_of_100(used: int, expected: int) -> None:
    assert strain_for(used, 100) == expected


@pytest.mark.parametrize(
    ("start", "free", "linear_end", "full"),
    [(100, 100, 130, 200), (10, 10, 40, 110), (130, 130, 160, 230)],
)
def test_every_threshold_moves_with_the_start(
    start: int, free: int, linear_end: int, full: int
) -> None:
    assert strain_for(free, start) == 0
    assert strain_for(free + 1, start) == 1
    assert strain_for(linear_end, start) == 30
    assert strain_for(full, start) == 90
    assert redline(start) == full


def test_a_quiet_history_starts_at_the_base() -> None:
    result = outlook([], TODAY)
    assert (result.strain, result.start, result.low, result.high) == (0, 100, 10, 100)


def test_spending_past_the_start_lowers_tomorrows_start() -> None:
    result = outlook([day(1, 100, 130)], TODAY)
    assert (result.strain, result.start) == (30, 70)


def test_the_override_after_strain_may_raise_the_start_to_60_at_most() -> None:
    result = outlook([day(1, 100, 192)], TODAY)
    assert (result.start, result.low, result.high) == (11, 10, 60)


def test_strain_recovers_30_a_day_and_rest_days_count() -> None:
    assert outlook([day(1, 100, 200)], TODAY).start == 10
    assert outlook([day(2, 100, 200)], TODAY).start == 40
    assert outlook([day(3, 100, 200)], TODAY).start == 70
    assert outlook([day(4, 100, 200)], TODAY).start == 100


def test_past_the_redline_tomorrow_is_exactly_10_with_no_override() -> None:
    result = outlook([day(1, 100, 201)], TODAY)
    assert (result.start, result.low, result.high) == (10, 10, 10)
    assert outlook([day(2, 100, 201)], TODAY).start == 40


def test_the_redline_moves_with_a_low_start() -> None:
    assert outlook([day(1, 10, 110)], TODAY).start == 10
    assert outlook([day(1, 10, 111)], TODAY).high == 10
    assert outlook([day(1, 10, 110)], TODAY).high == 60


def test_unspent_qi_becomes_a_bonus_of_at_most_30() -> None:
    assert outlook([day(1, 100, 90)], TODAY).start == 110
    assert outlook([day(1, 100, 20)], TODAY).start == 130
    assert outlook([day(1, 100, 100)], TODAY).start == 100


def test_the_bonus_does_not_need_a_sealed_or_finished_day() -> None:
    assert outlook([], TODAY).start == 100
    assert outlook([day(3, 100, 0)], TODAY).start == 130


def test_an_unused_day_restores_30_either_way() -> None:
    assert outlook([day(2, 100, 150)], TODAY).start == 56  # 74 strain, minus 30 for the rest day
    assert outlook([day(2, 100, 80)], TODAY).start == 130


def test_a_bonus_start_can_be_lowered_but_not_beyond_what_is_offered() -> None:
    result = outlook([day(1, 100, 0)], TODAY)
    assert (result.start, result.high) == (130, 130)


def test_no_bonus_while_strain_remains() -> None:
    assert outlook([day(2, 100, 200), day(1, 10, 0)], TODAY).start == 40


def test_a_day_spent_recovering_earns_no_bonus() -> None:
    # 120 spent -> strain 20; the next day starts at 80, rests, and is back at exactly 100.
    assert outlook([day(2, 100, 120), day(1, 80, 0)], TODAY).start == 100


def test_a_bonus_needs_a_day_that_began_without_strain() -> None:
    assert outlook([day(1, 40, 0)], TODAY).start == 130


def test_old_history_is_only_a_week_of_rest() -> None:
    assert outlook([day(30, 100, 200)], TODAY).start == 130


def test_preview_of_tomorrow() -> None:
    assert next_start(0, 100, 130) == 70
    assert next_start(0, 100, 201) == 10
    assert next_start(0, 100, 40) == 130


def test_a_chosen_start_must_be_inside_the_range() -> None:
    available = outlook([day(1, 100, 200)], TODAY)
    assert choose_start(60, available) == 60
    with pytest.raises(QiError):
        choose_start(61, available)
    with pytest.raises(QiError):
        choose_start(9, available)


def test_qi_text_is_blank_or_a_whole_number_up_to_100() -> None:
    assert parse_qi("") is None
    assert parse_qi(" 40 ") == 40
    assert parse_qi("100") == 100
    for bad in ("101", "-1", "4.5", "lots"):
        with pytest.raises(QiError):
            parse_qi(bad)


def test_restorative_arts_give_qi_back() -> None:
    trials = [
        make_trial("a", qi_expected=40, state=TrialState.DONE),
        make_trial("b", qi_expected=15, state=TrialState.DONE, art_kind=ArtKind.RESTORATIVE),
        make_trial("c", qi_expected=30),
    ]
    assert spent(trials) == 25
    assert planned(trials) == 55


def test_net_qi_never_goes_below_zero_and_blank_counts_as_zero() -> None:
    rest = make_trial("r", qi_expected=50, state=TrialState.DONE, art_kind=ArtKind.RESTORATIVE)
    assert spent([rest, make_trial("x", state=TrialState.DONE)]) == 0


def test_the_gauge_fills_calm_first_then_surge_then_redline() -> None:
    assert gauge_fill(60, 100) == GaugeFill(calm=60, surge=0, redline=0)
    assert gauge_fill(120, 100) == GaugeFill(calm=100, surge=20, redline=0)
    assert gauge_fill(150, 100) == GaugeFill(calm=100, surge=30, redline=20)


def test_the_gauge_stops_filling_at_the_redline() -> None:
    assert gauge_fill(500, 100) == GaugeFill(calm=100, surge=30, redline=70)


def test_the_gauge_follows_a_lower_start() -> None:
    assert gauge_fill(60, 40) == GaugeFill(calm=40, surge=20, redline=0)


@given(st.text())
def test_any_qi_text_gives_a_number_or_a_qi_error(text: str) -> None:
    try:
        result = parse_qi(text)
    except QiError:
        return
    assert result is None or 0 <= result <= 100


def test_qi_text_takes_ascii_digits_only() -> None:
    for bad in ("\u00b2", "\u0663", "\uff14"):
        with pytest.raises(QiError):
            parse_qi(bad)
