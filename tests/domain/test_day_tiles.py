from datetime import datetime, timedelta

import pytest

from scrolly.domain.day_tiles import SLIVER_PCT, TileState, essence_tiles, qi_row
from scrolly.domain.models import ArtKind, TrialState
from tests.factories import make_trial

NOW = datetime.fromisoformat("2026-10-22T13:00:00+02:00")


def test_tiles_run_conquered_by_time_then_the_trial_at_hand_then_the_queue() -> None:
    trials = [
        make_trial("Waiting B", position=2, essence_expected_min=10),
        make_trial("Later", state=TrialState.DONE, completed_at=NOW, essence_actual_min=10),
        make_trial("Now", state=TrialState.IMMEDIATE, essence_expected_min=10),
        make_trial("Waiting A", position=1, essence_expected_min=10),
        make_trial(
            "Earlier",
            state=TrialState.DONE,
            completed_at=NOW - timedelta(hours=1),
            essence_actual_min=10,
        ),
    ]
    tiles = essence_tiles(trials)
    assert [t.title for t in tiles] == ["Earlier", "Later", "Now", "Waiting A", "Waiting B"]
    assert [t.state for t in tiles] == [TileState.DONE] * 2 + [TileState.NOW] + [
        TileState.WAITING
    ] * 2


def test_a_conquered_trial_weighs_what_it_took_an_open_one_its_estimate() -> None:
    done = make_trial(
        "Report", state=TrialState.DONE, essence_expected_min=60, essence_actual_min=90
    )
    tiles = essence_tiles([done, make_trial("Call", essence_expected_min=30)])
    assert [t.share_pct for t in tiles] == pytest.approx([75.0, 25.0])
    assert (tiles[0].taken, tiles[0].planned) == ("1h30m", "1h")
    assert (tiles[1].taken, tiles[1].planned) == (None, "30m")


def test_a_trial_without_an_estimate_is_a_sliver_and_the_rest_share_what_is_left() -> None:
    tiles = essence_tiles([make_trial("Known", essence_expected_min=30), make_trial("Unknown")])
    assert tiles[1].share_pct == SLIVER_PCT
    assert sum(t.share_pct for t in tiles) == pytest.approx(100.0)
    assert tiles[1].planned is None


def test_qi_tiles_sit_on_a_scale_that_shows_the_room_before_the_start() -> None:
    row = qi_row([make_trial("Report", qi_expected=40)], start=100)
    assert row.tiles[0].share_pct == pytest.approx(40 / 130 * 100)
    assert row.harmonious_pct == pytest.approx(100 / 130 * 100)
    assert row.igniting_pct == pytest.approx(100.0)


def test_a_day_past_the_igniting_stretch_grows_the_scale_and_restorative_arts_weigh_nothing() -> (
    None
):
    rest = make_trial("Nap", qi_expected=20, art_kind=ArtKind.RESTORATIVE)
    row = qi_row([make_trial("Big", qi_expected=200), rest], start=100)
    assert row.harmonious_pct == pytest.approx(50.0)
    assert row.igniting_pct == pytest.approx(65.0)
    assert row.tiles[1].share_pct == SLIVER_PCT
