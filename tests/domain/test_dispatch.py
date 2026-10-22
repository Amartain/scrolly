from datetime import date, datetime

from scrolly.domain.beside import Beside
from scrolly.domain.dispatch import BESIDE, DispatchOptions, render_dispatch
from scrolly.domain.legend import DEFAULT_LEGEND, build_legend, with_symbol
from scrolly.domain.models import ArtKind, TrialState
from scrolly.io.import_discord_md import parse_discord_md
from tests.factories import make_trial

DAY = date(2026, 10, 19)
NOON = datetime.fromisoformat("2026-10-19T12:00:00+02:00")


def _trials() -> list:  # type: ignore[type-arg]
    return [
        make_trial(
            "Swedish podcast + coffee",
            state=TrialState.DONE,
            art_kind=ArtKind.FOUNDATIONAL,
            essence_expected_min=40,
            essence_actual_min=40,
            completed_at=NOON,
        ),
        make_trial(
            "Breakfast",
            state=TrialState.DONE,
            art_kind=ArtKind.RESTORATIVE,
            essence_expected_min=30,
            essence_actual_min=30,
            completed_at=NOON.replace(hour=13),
        ),
        make_trial("Combined session", state=TrialState.IMMEDIATE, essence_expected_min=30),
        make_trial("Repair Step 4", is_mandate=True, position=1, essence_expected_min=60),
        make_trial("Unestimated", position=2),
        make_trial("Moved on", state=TrialState.POSTPONED),
        make_trial("Let go", state=TrialState.LOST),
    ]


def test_the_scroll_follows_the_owners_format() -> None:
    text = render_dispatch(DAY, _trials(), DEFAULT_LEGEND, DispatchOptions())
    assert text.splitlines() == [
        "# :scroll: Scroll of Heavenly Tribulations and Ascendent Trials",
        "",
        "19/10/2026",
        "EXPECTED: 2h40m",
        "PROGRESS: 1h10m / 2h40m",
        "## Done",
        ":leaves: :scroll: Swedish podcast + coffee (40m) >> 40m",
        ":leaves: :herb: Breakfast (30m) >> 30m",
        "## Next",
        ":droplet: :white_circle: Combined session (30m)",
        "## Remaining",
        ":cloud: :lotus: Repair Step 4 (1h)",
        ":cloud: :white_circle: Unestimated",
        ":cloud: :zzz:",
        ":cloud: ENDE",
    ]


def test_the_dnd_line_opens_and_closes_the_scroll() -> None:
    lines = render_dispatch(DAY, _trials(), DEFAULT_LEGEND, DispatchOptions(dnd=True)).splitlines()
    assert lines[3] == "----- NO CHECK IN DND :crescent_moon:  -----"
    assert lines[-1] == lines[3] and lines[-2] == ""


def test_postponed_and_abandoned_lines_are_optional() -> None:
    plain = render_dispatch(DAY, _trials(), DEFAULT_LEGEND, DispatchOptions())
    assert "Postponed" not in plain and "Abandoned" not in plain
    both = render_dispatch(
        DAY,
        _trials(),
        DEFAULT_LEGEND,
        DispatchOptions(include_postponed=True, include_abandoned=True),
    )
    assert "Postponed: Moved on" in both and "Abandoned: Let go" in both


def test_the_users_own_symbols_are_used() -> None:
    legend = build_legend(with_symbol({}, "states", "done", None, ":seedling:"))
    text = render_dispatch(DAY, _trials(), legend, DispatchOptions())
    assert ":seedling: :scroll: Swedish podcast + coffee (40m) >> 40m" in text
    assert ":leaves:" not in text


def test_an_empty_day_is_still_a_valid_scroll() -> None:
    text = render_dispatch(DAY, [], DEFAULT_LEGEND, DispatchOptions())
    assert "EXPECTED: 0m" in text and text.endswith(":cloud: ENDE\n")


def test_the_importer_reads_the_scroll_back() -> None:
    text = render_dispatch(DAY, _trials(), DEFAULT_LEGEND, DispatchOptions(dnd=True))
    batch = parse_discord_md(text)
    assert [(t.title, t.essence_actual_min) for t in batch.trials] == [
        ("Swedish podcast + coffee", 40),
        ("Breakfast", 30),
    ]
    assert all(t.logical_day == DAY for t in batch.trials)


def test_time_run_beside_another_trial_is_marked_counted_and_reads_back() -> None:
    trials = _trials()
    podcast, breakfast = trials[0], trials[1]
    beside = {breakfast.id: Beside(minutes=25, partner_id=podcast.id)}
    text = render_dispatch(DAY, trials, DEFAULT_LEGEND, DispatchOptions(), beside, focus_min=45)
    lines = text.splitlines()
    assert "PROGRESS: 1h10m / 2h40m (25m beside)" in lines
    assert "FOCUS: 45m" in lines
    assert f":leaves: :herb: Breakfast (30m) >> 30m {BESIDE} Swedish podcast + coffee" in lines
    assert ":leaves: :scroll: Swedish podcast + coffee (40m) >> 40m" in lines
    batch = parse_discord_md(text)
    assert [(t.title, t.essence_actual_min) for t in batch.trials] == [
        ("Swedish podcast + coffee", 40),
        ("Breakfast", 30),
    ]


def test_without_time_beside_the_summary_stays_as_it_was() -> None:
    text = render_dispatch(DAY, _trials(), DEFAULT_LEGEND, DispatchOptions(), {}, focus_min=70)
    assert "FOCUS" not in text
    assert "beside" not in text
