from datetime import date
from pathlib import Path

import pytest

from scrolly.domain.merge import ImportBatch
from scrolly.domain.models import OriginType, TrialState
from scrolly.io.errors import ImportFormatError
from scrolly.io.import_discord_md import parse_discord_md
from scrolly.io.importers import parse_upload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "quest_board.md"


@pytest.fixture
def batch() -> ImportBatch:
    return parse_discord_md(FIXTURE.read_text(encoding="utf-8"))


def test_only_done_lines_become_trials_even_after_a_stray_character(batch: ImportBatch) -> None:
    assert len(batch.trials) == 6
    assert all(t.state is TrialState.DONE for t in batch.trials)
    titles = {t.title for t in batch.trials}
    assert "Evening yoga" not in titles and "ENDE" not in titles


def test_days_are_read_as_day_month_year(batch: ImportBatch) -> None:
    assert {t.logical_day for t in batch.trials} == {date(2026, 10, 14), date(2026, 10, 16)}


def test_type_shortcodes_map_to_mandate_and_origin(batch: ImportBatch) -> None:
    by_title = {t.title: t for t in batch.trials}
    assert by_title["Morning stretch"].origin_type is OriginType.FOUNDATIONAL_ART
    assert by_title["Tea break"].origin_type is OriginType.RESTORATIVE_ART
    assert by_title["Plan the week"].is_mandate
    assert not by_title["Walk (with dog)"].is_mandate


def test_titles_keep_other_shortcodes_and_parentheses(batch: ImportBatch) -> None:
    titles = {t.title for t in batch.trials}
    assert "Send invoice in :scroll: the tool" in titles
    assert "Walk (with dog)" in titles


def test_expected_and_actual_minutes(batch: ImportBatch) -> None:
    walk = next(t for t in batch.trials if t.title.startswith("Walk"))
    assert (walk.essence_expected_min, walk.essence_actual_min) == (15, 73)
    chore = next(t for t in batch.trials if t.title == "Untyped chore")
    assert (chore.essence_expected_min, chore.essence_actual_min) == (None, 10)


def test_ids_are_stable(batch: ImportBatch) -> None:
    again = parse_discord_md(FIXTURE.read_text(encoding="utf-8"))
    assert [t.id for t in batch.trials] == [t.id for t in again.trials]
    assert len({t.id for t in batch.trials}) == len(batch.trials)


def test_text_without_a_quest_board_is_rejected() -> None:
    with pytest.raises(ImportFormatError):
        parse_discord_md("just some notes")


def test_the_scroll_of_heavenly_tribulations_is_read_like_a_quest_board() -> None:
    text = (FIXTURE.parent / "heavenly_scroll.md").read_text(encoding="utf-8")
    trials = parse_discord_md(text).trials
    assert [t.title for t in trials] == ["Swedish podcast + coffee", "Breakfast", "Feeding the cat"]
    assert {t.logical_day for t in trials} == {date(2026, 10, 19)}
    assert [t.origin_type for t in trials] == [
        OriginType.FOUNDATIONAL_ART,
        OriginType.RESTORATIVE_ART,
        OriginType.BRAIN_DUMP,
    ]
    assert [t.essence_actual_min for t in trials] == [40, 30, 10]


@pytest.mark.parametrize("spelling", ["Ascendent", "Ascendant"])
def test_both_spellings_of_the_scroll_title_are_accepted(spelling: str) -> None:
    title = f"# Scroll of Heavenly Tribulations and {spelling} Trials"
    text = f"{title}\n1/2/2026\n## Done\n:leaves: Tidy (5m) >> 5m\n"
    assert len(parse_discord_md(text).trials) == 1


def test_upload_picks_the_parser_from_the_file_name() -> None:
    content = FIXTURE.read_bytes()
    assert len(parse_upload("board.MD", content).trials) == 6
    with pytest.raises(ImportFormatError):
        parse_upload("board.zip", content)
    with pytest.raises(ImportFormatError):
        parse_upload("board.md", b"\xff\xfe\x00bad")
