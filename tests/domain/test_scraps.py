from datetime import datetime, timedelta

from scrolly.domain.scraps import (
    Scrap,
    close_after_crash,
    close_scrap,
    is_kept,
    note_trial,
    open_scrap,
    scrap_lanes,
    visit_seconds,
    write_scrap,
)
from scrolly.domain.segments import Discipline, Segment

OPENED = datetime.fromisoformat("2026-10-21T14:00:00+02:00")


def _later(minutes: int) -> datetime:
    return OPENED + timedelta(minutes=minutes)


def test_a_scrap_with_nothing_written_is_not_kept() -> None:
    scrap = open_scrap("s", OPENED)
    assert not is_kept(scrap)
    assert not is_kept(write_scrap(scrap, "  \n ", _later(1)))
    assert is_kept(write_scrap(scrap, "call the bank", _later(1)))


def test_writing_remembers_when_it_was_last_saved() -> None:
    scrap = write_scrap(open_scrap("s", OPENED), "idea", _later(7))
    assert (scrap.text, scrap.saved_at) == ("idea", _later(7))


def test_trials_are_noted_in_order_of_first_start_without_repeats() -> None:
    scrap = open_scrap("s", OPENED)
    for trial_id in ("a", "b", "a", "c", "b"):
        scrap = note_trial(scrap, trial_id)
    assert scrap.trial_ids == ("a", "b", "c")


def test_leaving_closes_the_scrap_once() -> None:
    closed = close_scrap(open_scrap("s", OPENED), _later(30))
    assert closed.closed_at == _later(30)
    assert close_scrap(closed, _later(90)).closed_at == _later(30)


def test_a_scrap_found_open_after_a_crash_ends_where_it_was_last_saved() -> None:
    scrap = write_scrap(open_scrap("s", OPENED), "idea", _later(12))
    assert close_after_crash(scrap).closed_at == _later(12)
    assert scrap.is_open


def _segment(trial_id: str, start: int, end: int | None) -> Segment:
    ended = None if end is None else _later(end)
    return Segment(f"{trial_id}{start}", trial_id, Discipline.INCENSE, _later(start), ended)


def _visit(*trial_ids: str) -> Scrap:
    scrap = open_scrap("s", _later(10))
    for trial_id in trial_ids:
        scrap = note_trial(scrap, trial_id)
    return close_scrap(scrap, _later(70))


def test_a_visit_lasts_from_opening_to_closing_and_an_open_one_has_no_length() -> None:
    assert visit_seconds(_visit()) == 3600
    assert visit_seconds(open_scrap("s", OPENED)) == 0


def test_a_lane_per_trial_in_the_order_started_cut_to_the_visit() -> None:
    scrap = _visit("main", "side")  # 14:10 to 15:10
    segments = {
        "main": [_segment("main", 0, 30), _segment("main", 40, 90)],  # starts before, ends after
        "side": [_segment("side", 20, None)],  # still running when the visit closed
    }
    main, side = scrap_lanes(scrap, segments)
    assert (main.trial_id, side.trial_id) == ("main", "side")
    assert main.spans == ((0, 1200), (1800, 3600))
    assert side.spans == ((600, 3600),)


def test_trials_worked_side_by_side_overlap_in_their_lanes() -> None:
    scrap = _visit("main", "side")
    segments = {"main": [_segment("main", 10, 60)], "side": [_segment("side", 30, 50)]}
    main, side = scrap_lanes(scrap, segments)
    assert main.spans == ((0, 3000),) and side.spans == ((1200, 2400),)


def test_a_trial_with_no_time_in_the_visit_still_has_its_lane_and_an_open_scrap_has_none() -> None:
    lanes = scrap_lanes(_visit("quiet"), {"quiet": [_segment("quiet", 0, 5)]})
    assert [lane.spans for lane in lanes] == [()]
    assert scrap_lanes(open_scrap("s", OPENED), {}) == []
