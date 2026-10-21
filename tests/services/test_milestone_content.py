from scrolly.services.milestone_content import load_milestones, load_quotes


def test_the_shipped_milestones_follow_the_features_table() -> None:
    rows = load_milestones()
    assert [r.day for r in rows] == [3, 7, 10, 14, 21, 30, 60, 100]
    day_21 = next(r for r in rows if r.day == 21)
    assert day_21.quote is None and day_21.banner is not None
    assert next(r for r in rows if r.day == 100).quote is not None


def test_only_day_100_is_a_glitch() -> None:
    assert [r.day for r in load_milestones() if r.style == "glitch"] == [100]


def test_every_stand_in_quote_is_marked_and_has_no_author() -> None:
    quotes = load_quotes()
    assert len(quotes) >= 30
    assert all(q.stand_in and q.attribution is None and q.text.strip() for q in quotes)
    assert len({q.text for q in quotes}) == len(quotes)
