import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import Art, ArtKind, OriginType, PlanStatus, TrialState
from scrolly.domain.planning import PlanningError
from scrolly.ports import Store
from scrolly.services.planning_view import build_planning_view
from tests.factories import DAY, make_item
from tests.services.flow import Flow


@pytest.fixture
def flow(store: Store, clock: FixedClock) -> Flow:
    return Flow(store, clock)


def _plan_two_lines(flow: Flow) -> None:
    flow.planning.start()
    flow.planning.save_text("Write report\n\nTidy desk\n")
    flow.planning.proceed()


def test_a_fresh_day_is_the_zero_state_and_start_opens_phase_one(flow: Flow) -> None:
    assert flow.status() is PlanStatus.ZERO
    flow.planning.start()
    assert flow.status() is PlanStatus.INSCRIBE


def test_start_twice_keeps_the_text(flow: Flow) -> None:
    flow.planning.start()
    flow.planning.save_text("keep me")
    flow.planning.start()
    assert build_planning_view(flow.store, DAY).text == "keep me"


def test_proceed_turns_lines_into_ordered_mortal_trials_and_clears_the_text(flow: Flow) -> None:
    _plan_two_lines(flow)
    view = build_planning_view(flow.store, DAY)
    assert (view.status, view.text) == (PlanStatus.ESTIMATE, "")
    assert flow.titles() == ["Write report", "Tidy desk"]
    assert all(not t.is_mandate for t in view.trials)


def test_proceed_with_an_empty_scroll_is_refused(flow: Flow) -> None:
    flow.planning.start()
    flow.planning.save_text("  \n \n")
    with pytest.raises(PlanningError):
        flow.planning.proceed()
    assert flow.status() is PlanStatus.INSCRIBE


def test_steps_out_of_order_are_refused(flow: Flow) -> None:
    with pytest.raises(PlanningError):
        flow.planning.proceed()
    flow.planning.start()
    with pytest.raises(PlanningError):
        flow.planning.seal()
    with pytest.raises(PlanningError):
        flow.planning.back()


def test_summoning_a_horizon_item_moves_it_onto_the_scroll(flow: Flow) -> None:
    flow.store.horizon.replace_all([make_item("Plan", id="h1", is_mandate=True)], flow.clock.now())
    flow.planning.start()
    flow.scroll.summon("horizon", "h1")
    (trial,) = build_planning_view(flow.store, DAY).trials
    assert trial.is_mandate and (trial.origin_type, trial.origin_id) == (OriginType.HORIZON, "h1")
    assert flow.store.horizon.list_all() == []


def test_summoning_an_art_copies_it_and_the_template_stays(flow: Flow) -> None:
    art = Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch", essence_expected_min=15)
    flow.store.arts.save([art], flow.clock.now())
    flow.planning.start()
    flow.scroll.summon("art", "a1")
    flow.scroll.summon("art", "a1")
    assert flow.titles() == ["Stretch", "Stretch"]
    assert flow.store.arts.list_all() == [art]


def test_summoning_something_missing_is_refused(flow: Flow) -> None:
    flow.planning.start()
    with pytest.raises(PlanningError):
        flow.scroll.summon("horizon", "nope")
    with pytest.raises(PlanningError):
        flow.scroll.summon("art", "nope")


def test_unstaging_returns_the_horizon_item_and_removes_the_trial(flow: Flow) -> None:
    flow.store.horizon.replace_all([make_item("Plan", id="h1")], flow.clock.now())
    flow.planning.start()
    flow.scroll.summon("horizon", "h1")
    (trial,) = build_planning_view(flow.store, DAY).trials
    flow.scroll.unstage(trial.id)
    assert [i.id for i in flow.store.horizon.list_all()] == ["h1"]
    assert flow.titles() == []


def test_back_to_inscribing_keeps_every_trial_and_estimate(flow: Flow) -> None:
    _plan_two_lines(flow)
    (first, _second) = build_planning_view(flow.store, DAY).trials
    flow.scroll.update(first.id, "1h15m", True)
    flow.planning.back()
    assert flow.status() is PlanStatus.INSCRIBE
    flow.planning.save_text("Third")
    flow.planning.proceed()
    trials = build_planning_view(flow.store, DAY).trials
    assert [t.title for t in trials] == ["Write report", "Tidy desk", "Third"]
    assert trials[0].essence_expected_min == 75 and trials[0].is_mandate


def test_a_forgotten_trial_is_appended_and_a_blank_one_refused(flow: Flow) -> None:
    _plan_two_lines(flow)
    flow.scroll.add("  Call mum ")
    assert flow.titles()[-1] == "Call mum"
    with pytest.raises(PlanningError):
        flow.scroll.add("   ")


def test_update_changes_only_what_is_sent_and_blank_clears_the_estimate(flow: Flow) -> None:
    _plan_two_lines(flow)
    (first, _second) = build_planning_view(flow.store, DAY).trials
    flow.scroll.update(first.id, "45m", None)
    flow.scroll.update(first.id, None, True)
    trial = build_planning_view(flow.store, DAY).trials[0]
    assert (trial.essence_expected_min, trial.is_mandate) == (45, True)
    flow.scroll.update(first.id, "", None)
    assert build_planning_view(flow.store, DAY).trials[0].essence_expected_min is None


def test_dismissing_a_mandate_goes_to_the_horizon_and_a_mortal_is_lost(flow: Flow) -> None:
    _plan_two_lines(flow)
    (first, second) = build_planning_view(flow.store, DAY).trials
    flow.scroll.update(first.id, None, True)
    flow.scroll.dismiss(first.id)
    flow.scroll.dismiss(second.id)
    assert [i.title for i in flow.store.horizon.list_all()] == ["Write report"]
    states = {t.title: t.state for t in flow.store.trials.list_for_day(DAY)}
    assert states == {"Write report": TrialState.POSTPONED, "Tidy desk": TrialState.LOST}
    assert flow.titles() == []


def test_reorder_changes_the_seal_order(flow: Flow) -> None:
    _plan_two_lines(flow)
    first, second = build_planning_view(flow.store, DAY).trials
    flow.scroll.reorder([second.id, first.id])
    assert flow.titles() == ["Tidy desk", "Write report"]
    flow.planning.seal()
    trials = build_planning_view(flow.store, DAY).trials
    assert [(t.title, t.state) for t in trials] == [
        ("Tidy desk", TrialState.IMMEDIATE),
        ("Write report", TrialState.REMAINING),
    ]


def test_reorder_with_a_wrong_id_list_is_refused(flow: Flow) -> None:
    _plan_two_lines(flow)
    with pytest.raises(PlanningError):
        flow.scroll.reorder(["nope"])


def test_seal_starts_the_day_once_and_ends_planning(flow: Flow) -> None:
    _plan_two_lines(flow)
    flow.planning.seal()
    assert flow.status() is PlanStatus.ACTIVE
    day = flow.store.days.get(DAY)
    assert day is not None and day.first_sealed_at == flow.clock.now()
    assert flow.store.drafts.get() is None


def test_sealing_when_everything_was_dismissed_is_refused(flow: Flow) -> None:
    _plan_two_lines(flow)
    for trial in build_planning_view(flow.store, DAY).trials:
        flow.scroll.dismiss(trial.id)
    with pytest.raises(PlanningError):
        flow.planning.seal()


def test_abandon_gives_the_horizon_back_exactly_and_returns_to_zero(flow: Flow) -> None:
    before = [make_item("Plan", id="h1"), make_item("Read", id="h2")]
    flow.store.horizon.replace_all(before, flow.clock.now())
    flow.planning.start()
    flow.scroll.summon("horizon", "h1")
    flow.planning.save_text("a line")
    flow.planning.proceed()
    flow.planning.abandon()
    assert flow.status() is PlanStatus.ZERO
    assert {i.id for i in flow.store.horizon.list_all()} == {"h1", "h2"}
    assert flow.store.trials.list_for_day(DAY) == []
