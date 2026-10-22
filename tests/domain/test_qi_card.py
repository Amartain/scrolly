from scrolly.domain.models import ArtKind, TrialState
from scrolly.domain.qi_card import QiChoices, qi_choices, spent_if
from tests.factories import make_trial


def test_choices_are_half_the_estimate_and_half_again() -> None:
    assert qi_choices(40) == QiChoices(lighter=20, foreseen=40, heavier=60)


def test_a_small_estimate_still_has_a_heavier_answer() -> None:
    assert qi_choices(0) == QiChoices(0, 0, 5)
    assert qi_choices(2) == QiChoices(1, 2, 7)


def test_heavier_never_passes_the_most_a_trial_can_take() -> None:
    assert qi_choices(90).heavier == 100


def test_spent_if_counts_the_answer_in_place_of_what_was_recorded() -> None:
    done = make_trial("A", state=TrialState.DONE, qi_expected=30, qi_actual=30)
    other = make_trial("B", state=TrialState.DONE, qi_expected=10, qi_actual=10)
    assert spent_if([done, other], done.id, 50) == 60


def test_spent_if_a_restorative_art_restores_what_is_answered() -> None:
    work = make_trial("A", state=TrialState.DONE, qi_expected=40, qi_actual=40)
    rest = make_trial(
        "Tea", state=TrialState.DONE, art_kind=ArtKind.RESTORATIVE, qi_expected=10, qi_actual=10
    )
    assert spent_if([work, rest], rest.id, 25) == 15
