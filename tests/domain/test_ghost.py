from datetime import datetime, timedelta

from scrolly.domain.ghost import is_ghost_gap, needs_note

NOW = datetime.fromisoformat("2026-10-21T14:00:00+02:00")


def test_more_than_an_hour_and_a_half_away_is_a_silence() -> None:
    assert is_ghost_gap(NOW - timedelta(minutes=91), NOW)
    assert is_ghost_gap(NOW - timedelta(hours=9), NOW)


def test_an_hour_and_a_half_or_less_is_not() -> None:
    assert not is_ghost_gap(NOW - timedelta(minutes=90), NOW)
    assert not is_ghost_gap(NOW - timedelta(minutes=5), NOW)


def test_the_very_first_visit_has_no_silence() -> None:
    assert not is_ghost_gap(None, NOW)


def test_last_seen_is_written_at_most_every_thirty_seconds() -> None:
    assert not needs_note(NOW - timedelta(seconds=5), NOW, pending=False)
    assert not needs_note(NOW - timedelta(seconds=29), NOW, pending=False)
    assert needs_note(NOW - timedelta(seconds=30), NOW, pending=False)
    assert needs_note(NOW - timedelta(minutes=5), NOW, pending=False)


def test_a_first_visit_or_a_waiting_question_is_always_written() -> None:
    assert needs_note(None, NOW, pending=False)
    assert needs_note(NOW - timedelta(seconds=1), NOW, pending=True)
