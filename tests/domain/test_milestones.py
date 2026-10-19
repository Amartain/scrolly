from scrolly.domain.milestones import MilestoneRow, Quote, milestone_for

QUOTES = [Quote(f"q{i}", stand_in=True) for i in range(5)]
ROWS = [
    MilestoneRow(3, Quote("Own words", "Someone")),
    MilestoneRow(21, None, "Day 21 Milestone"),
    MilestoneRow(10, Quote("Ten", "Ten Author"), "Day 10 Milestone"),
]


def test_a_milestone_day_uses_its_own_quote() -> None:
    reached = milestone_for(3, ROWS, QUOTES)
    assert reached.quote == Quote("Own words", "Someone") and reached.banner is None


def test_a_milestone_without_a_quote_takes_the_rotation_and_keeps_its_banner() -> None:
    reached = milestone_for(21, ROWS, QUOTES)
    assert reached.quote == QUOTES[21 % 5] and reached.banner == "Day 21 Milestone"


def test_a_milestone_with_both_keeps_both() -> None:
    reached = milestone_for(10, ROWS, QUOTES)
    assert (reached.quote.text, reached.banner) == ("Ten", "Day 10 Milestone")


def test_other_days_rotate_through_the_quotes_and_never_change_for_a_day() -> None:
    seen = [milestone_for(day, ROWS, QUOTES).quote.text for day in range(4, 9)]
    assert seen == ["q4", "q0", "q1", "q2", "q3"]
    assert milestone_for(5, ROWS, QUOTES) == milestone_for(5, ROWS, QUOTES)
    assert milestone_for(5, ROWS, QUOTES).banner is None


def test_the_cycle_count_travels_with_the_milestone() -> None:
    assert milestone_for(12, ROWS, QUOTES).cycles == 12
