import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import Art, ArtKind, OriginType
from scrolly.domain.uniqueness import DuplicateTitleError
from scrolly.ports import Store
from scrolly.services.horizon import HorizonService
from tests.factories import DAY, make_item
from tests.services.flow import Flow, by_title, seal_day


def test_phase_one_blocks_a_repeated_line_and_keeps_the_text(
    store: Store, clock: FixedClock
) -> None:
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("Walk\nwalk")
    with pytest.raises(DuplicateTitleError, match="Written twice: walk"):
        flow.planning.proceed()
    assert store.trials.list_for_day(DAY) == []


def test_phase_one_blocks_a_title_on_the_horizon(store: Store, clock: FixedClock) -> None:
    store.horizon.replace_all([make_item("Taxes")], clock.now())
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("taxes")
    with pytest.raises(DuplicateTitleError, match="Already on the Horizon"):
        flow.planning.proceed()


def test_a_forgotten_trial_cannot_repeat_a_scroll_title(store: Store, clock: FixedClock) -> None:
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("Walk")
    flow.planning.proceed()
    with pytest.raises(DuplicateTitleError, match="Already on today's scroll"):
        flow.scroll.add("walk")


def test_scribe_refuses_a_horizon_title_and_a_scroll_title(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk")
    store.horizon.replace_all([make_item("Taxes")], clock.now())
    with pytest.raises(DuplicateTitleError, match="Already on the Horizon"):
        today.scribe("Taxes")
    with pytest.raises(DuplicateTitleError, match="Already on today's scroll"):
        today.scribe("WALK")


def test_a_conquered_title_is_still_taken(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk", "Read")
    today.conquer(by_title(store)["Walk"].id)
    with pytest.raises(DuplicateTitleError):
        today.scribe("Walk")


def test_a_fallen_leaf_can_be_entered_again(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk", "Read")
    today.abandon(by_title(store)["Read"].id)
    today.scribe("Read")


def test_horizon_add_and_rename_refuse_duplicates(store: Store, clock: FixedClock) -> None:
    seal_day(store, clock, "Walk")
    horizon = HorizonService(store, clock)
    horizon.add("Taxes")
    with pytest.raises(DuplicateTitleError, match="Already on today's scroll"):
        horizon.add("walk")
    with pytest.raises(DuplicateTitleError, match="Already on the Horizon"):
        horizon.add("TAXES")
    horizon.add("Mail")
    mail = next(i for i in store.horizon.list_all() if i.title == "Mail")
    with pytest.raises(DuplicateTitleError):
        horizon.edit(mail.id, title="Taxes")
    horizon.edit(mail.id, title="mail")  # its own title again is fine


def test_renaming_a_trial_refuses_a_taken_title(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk", "Read")
    store.horizon.replace_all([make_item("Taxes")], clock.now())
    read = by_title(store)["Read"]
    with pytest.raises(DuplicateTitleError):
        today.update(read.id, title="walk")
    with pytest.raises(DuplicateTitleError):
        today.update(read.id, title="Taxes")
    today.update(read.id, title="read")


def test_an_art_can_be_summoned_again_and_again(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk")
    store.arts.save([Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch")], clock.now())
    today.summon("art", "a1")
    today.summon("art", "a1")
    copies = [
        t for t in store.trials.list_for_day(DAY) if t.origin_type is OriginType.FOUNDATIONAL_ART
    ]
    assert [t.title for t in copies] == ["Stretch", "Stretch"]
    today.scribe("Stretch")  # an Art copy does not block a new trial
