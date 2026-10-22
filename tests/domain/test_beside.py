from datetime import datetime, timedelta

from scrolly.domain.beside import Beside, focus_minutes, time_beside
from scrolly.domain.segments import Discipline, Segment

T0 = datetime.fromisoformat("2026-10-22T09:00:00+02:00")


def _run(trial: str, discipline: Discipline, start: int, end: int | None) -> Segment:
    return Segment(
        id=f"{trial}-{start}",
        trial_id=trial,
        discipline=discipline,
        started_at=T0 + timedelta(minutes=start),
        ended_at=None if end is None else T0 + timedelta(minutes=end),
    )


def test_a_trial_run_beside_another_counts_its_minutes_and_finds_its_partner() -> None:
    segments = {
        "report": [_run("report", Discipline.INCENSE, 0, 60)],
        "call": [_run("call", Discipline.DASHBOARD, 70, 80)],
        "laundry": [_run("laundry", Discipline.PARALLEL, 10, 35)],
    }
    assert time_beside(segments, T0 + timedelta(hours=2)) == {"laundry": Beside(25, "report")}


def test_a_parallel_run_still_going_counts_up_to_now() -> None:
    segments = {"laundry": [_run("laundry", Discipline.PARALLEL, 0, None)]}
    assert time_beside(segments, T0 + timedelta(minutes=12)) == {"laundry": Beside(12, None)}


def test_focus_counts_overlapping_runs_once() -> None:
    segments = [
        _run("report", Discipline.INCENSE, 0, 60),
        _run("laundry", Discipline.PARALLEL, 10, 35),
        _run("call", Discipline.DASHBOARD, 70, 80),
    ]
    assert focus_minutes(segments, T0 + timedelta(hours=2)) == 70
    assert focus_minutes([], T0) == 0
