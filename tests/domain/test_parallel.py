from datetime import datetime

import pytest

from scrolly.domain.day_flow import TrialError, conquer, promote_next
from scrolly.domain.models import Art, ArtKind, Trial, TrialState
from scrolly.domain.parallel import MAX_CANDIDATES, Source, can_run_beside, find_candidates
from tests.factories import make_item, make_trial

NOW = datetime.fromisoformat("2026-10-21T14:00:00+02:00")


def _scroll() -> tuple[Trial, Trial, Trial]:
    main = make_trial("Write report", state=TrialState.IMMEDIATE, position=0)
    tea = make_trial("Tend the tea", state=TrialState.REMAINING, position=1)
    sweep = make_trial("Sweep the pavilion", state=TrialState.REMAINING, position=2)
    return main, tea, sweep


def test_the_search_offers_waiting_trials_then_arts_then_the_horizon() -> None:
    main, tea, _ = _scroll()
    arts = [Art("art-tea", ArtKind.FOUNDATIONAL, "Tea ceremony")]
    horizon = [make_item("Order tea leaves")]
    found = find_candidates("tea", [main, tea], arts, horizon, main.id)
    assert [(c.source, c.title) for c in found] == [
        (Source.REMAINING, "Tend the tea"),
        (Source.ART, "Tea ceremony"),
        (Source.HORIZON, "Order tea leaves"),
    ]


def test_the_search_ignores_case_and_blank_and_never_offers_the_trial_at_hand() -> None:
    main, tea, sweep = _scroll()
    assert find_candidates("  ", [main, tea], [], [], main.id) == []
    assert [c.id for c in find_candidates("SWEEP", [main, tea, sweep], [], [], main.id)] == [
        sweep.id
    ]
    assert find_candidates("report", [main, tea], [], [], main.id) == []


def test_the_search_stops_at_a_short_list() -> None:
    trials = [make_trial(f"Errand {n}", state=TrialState.REMAINING, position=n) for n in range(20)]
    assert len(find_candidates("errand", trials, [], [], None)) == MAX_CANDIDATES


def test_only_a_waiting_trial_other_than_the_main_one_can_run_beside_when_none_does() -> None:
    main, tea, _ = _scroll()
    assert can_run_beside(tea, main.id, None)
    assert not can_run_beside(main, main.id, None)
    assert not can_run_beside(tea, main.id, "someone-else")


def test_the_unfinished_parallel_trial_is_next_ahead_of_the_top_of_remaining() -> None:
    _, tea, sweep = _scroll()
    assert [t.id for t in promote_next([tea, sweep], sweep.id)] == [sweep.id]
    assert [t.id for t in promote_next([tea, sweep], None)] == [tea.id]
    assert [t.id for t in promote_next([tea, sweep], "finished-long-ago")] == [tea.id]


def test_a_parallel_trial_is_conquered_from_waiting_not_from_immediate() -> None:
    main, tea, _ = _scroll()
    assert conquer(tea, NOW, beside=True).state is TrialState.DONE
    with pytest.raises(TrialError):
        conquer(main, NOW, beside=True)
    with pytest.raises(TrialError):
        conquer(tea, NOW)
