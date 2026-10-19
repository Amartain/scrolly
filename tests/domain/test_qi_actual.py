from datetime import datetime
from typing import Any

import pytest

from scrolly.domain.day_flow import (
    TrialError,
    conquer,
    revive,
    set_actual_qi,
    set_estimated_qi,
)
from scrolly.domain.models import OriginType, Trial, TrialState
from scrolly.domain.qi import QiError, effective_qi, spent
from tests.factories import make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")


def _immediate(**fields: Any) -> Trial:
    return make_trial("Now", state=TrialState.IMMEDIATE, **fields)


def test_conquering_records_the_estimated_qi_as_the_actual() -> None:
    assert conquer(_immediate(qi_expected=40), NOW).qi_actual == 40


def test_conquering_a_trial_without_qi_records_nothing() -> None:
    assert conquer(_immediate(), NOW).qi_actual is None


def test_spent_counts_the_recorded_qi_not_the_estimate() -> None:
    done = conquer(_immediate(qi_expected=40), NOW)
    assert spent([set_actual_qi(done, "65")]) == 65


def test_a_blank_actual_falls_back_to_the_estimate() -> None:
    done = set_actual_qi(conquer(_immediate(qi_expected=40), NOW), "")
    assert done.qi_actual is None
    assert effective_qi(done) == 40
    assert spent([done]) == 40


def test_open_trials_count_at_their_estimate_even_if_an_actual_is_set() -> None:
    assert effective_qi(make_trial("x", qi_expected=30, qi_actual=99)) == 30


def test_a_restorative_art_restores_its_recorded_qi() -> None:
    art = conquer(
        _immediate(qi_expected=20, origin_type=OriginType.RESTORATIVE_ART),
        NOW,
    )
    work = set_actual_qi(conquer(_immediate(qi_expected=10), NOW), "50")
    assert spent([work, set_actual_qi(art, "15")]) == 35


def test_correcting_actual_qi_needs_a_conquered_trial_and_a_valid_figure() -> None:
    with pytest.raises(TrialError):
        set_actual_qi(_immediate(qi_expected=5), "5")
    done = conquer(_immediate(qi_expected=5), NOW)
    with pytest.raises(QiError):
        set_actual_qi(done, "lots")


def test_the_estimate_can_change_only_while_the_trial_is_open() -> None:
    assert set_estimated_qi(_immediate(qi_expected=5), "25").qi_expected == 25
    assert set_estimated_qi(_immediate(qi_expected=5), "").qi_expected is None
    with pytest.raises(TrialError):
        set_estimated_qi(conquer(_immediate(qi_expected=5), NOW), "25")


def test_reviving_clears_the_recorded_qi() -> None:
    done = conquer(_immediate(qi_expected=40), NOW)
    assert revive(done, [done]).qi_actual is None
