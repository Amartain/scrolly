import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import Art, ArtKind, OriginType
from scrolly.domain.uniqueness import DuplicateTitleError
from scrolly.ports import Store
from scrolly.services.horizon import HorizonService
from scrolly.services.today import TodayService
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


def _arts(store: Store, clock: FixedClock) -> None:
    arts = [
        Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Carry Water"),
        Art(id="a2", kind=ArtKind.RESTORATIVE, title="Nap"),
    ]
    store.arts.save(arts, clock.now())


def test_a_dump_line_naming_an_art_is_an_instance_and_may_repeat(
    store: Store, clock: FixedClock
) -> None:
    _arts(store, clock)
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("carry water\nCarry Water\nNap\nWalk")
    flow.planning.proceed()
    kinds = {t.title: t.art_kind for t in store.trials.list_for_day(DAY)}
    assert kinds == {
        "carry water": ArtKind.FOUNDATIONAL,
        "Carry Water": ArtKind.FOUNDATIONAL,
        "Nap": ArtKind.RESTORATIVE,
        "Walk": None,
    }


def test_phase_two_scribe_and_horizon_make_art_instances(store: Store, clock: FixedClock) -> None:
    _arts(store, clock)
    flow = Flow(store, clock)
    flow.planning.start()
    flow.planning.save_text("Walk")
    flow.planning.proceed()
    flow.scroll.add("Carry Water")
    flow.scroll.add("Carry Water")
    flow.planning.seal()
    today = TodayService(store, clock)
    today.scribe("nap")
    today.scribe("nap")
    HorizonService(store, clock).add("Carry Water")
    HorizonService(store, clock).add("Carry Water")
    marked = [t.art_kind for t in store.trials.list_for_day(DAY) if t.title != "Walk"]
    assert marked == [ArtKind.RESTORATIVE] * 2 + [ArtKind.FOUNDATIONAL] * 2
    assert [i.art_kind for i in store.horizon.list_all()] == [ArtKind.FOUNDATIONAL] * 2


def test_a_plain_title_is_still_refused_next_to_art_instances(
    store: Store, clock: FixedClock
) -> None:
    _arts(store, clock)
    today = seal_day(store, clock, "Walk")
    today.scribe("Carry Water")
    with pytest.raises(DuplicateTitleError):
        today.scribe("walk")


def test_renaming_into_and_out_of_an_art(store: Store, clock: FixedClock) -> None:
    _arts(store, clock)
    today = seal_day(store, clock, "Walk", "Read")
    walk = by_title(store)["Walk"]
    today.update(walk.id, is_mandate=True)
    today.update(walk.id, title="Nap")
    renamed = by_title(store)["Nap"]
    assert (renamed.art_kind, renamed.is_mandate) == (ArtKind.RESTORATIVE, False)
    today.update(renamed.id, title="Siesta")
    assert by_title(store)["Siesta"].art_kind is None


def test_a_horizon_art_instance_returns_when_unstaged(store: Store, clock: FixedClock) -> None:
    _arts(store, clock)
    HorizonService(store, clock).add("Nap")
    flow = Flow(store, clock)
    flow.planning.start()
    flow.scroll.summon("horizon", store.horizon.list_all()[0].id)
    staged = store.trials.list_for_day(DAY)[0]
    assert staged.art_kind is ArtKind.RESTORATIVE
    flow.scroll.unstage(staged.id)
    assert [(i.title, i.art_kind) for i in store.horizon.list_all()] == [
        ("Nap", ArtKind.RESTORATIVE)
    ]
