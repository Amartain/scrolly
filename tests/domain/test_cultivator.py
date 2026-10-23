from datetime import date

from scrolly.domain.cultivator import Cultivator, PeakFacts, settle_cultivator

DAY = date(2026, 10, 23)


def facts(
    *, running: bool = False, run: bool = False, left: bool = True, day: date = DAY
) -> PeakFacts:
    return PeakFacts(day=day, timer_running=running, run_under_way=run, trials_left=left)


UP = Cultivator(up=True, day=DAY)


def test_they_wait_at_the_foot_until_the_first_focus() -> None:
    assert settle_cultivator(Cultivator(), facts()).up is False


def test_a_running_timer_sends_them_up() -> None:
    assert settle_cultivator(Cultivator(), facts(running=True)).up is True


def test_a_run_under_way_keeps_them_up_through_its_breaks() -> None:
    assert settle_cultivator(Cultivator(), facts(run=True)).up is True


def test_a_pause_a_conquest_or_a_step_out_leaves_them_meditating() -> None:
    assert settle_cultivator(UP, facts()).up is True


def test_they_come_down_when_the_run_ends() -> None:
    during = settle_cultivator(UP, facts(run=True))
    assert settle_cultivator(during, facts()).up is False


def test_they_come_down_when_no_trials_are_left() -> None:
    assert settle_cultivator(UP, facts(left=False)).up is False


def test_they_come_down_at_the_days_turn() -> None:
    assert settle_cultivator(UP, facts(day=date(2026, 10, 24))).up is False


def test_a_new_focus_on_the_new_day_sends_them_up_again() -> None:
    assert settle_cultivator(UP, facts(running=True, day=date(2026, 10, 24))).up is True
