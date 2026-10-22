"""The card after a conquest: its three choices, and where the day's Qi lands for an answer.

Asked again as the answer changes, so the card can show the day's bar before anything is saved.
"""

from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.day_flow import TrialError
from scrolly.domain.logical_day import logical_day
from scrolly.domain.qi import check_qi
from scrolly.domain.qi_card import QiChoices, qi_choices, spent_if
from scrolly.ports import Store
from scrolly.services.golden_core import build_qi_view


@dataclass(frozen=True)
class QiCardView:
    choices: QiChoices
    spent: int  # the day's spent Qi with this answer
    start: int
    redline: int


def build_qi_card(store: Store, now: datetime, trial_id: str, value: int) -> QiCardView:
    trials = store.trials.list_for_day(logical_day(now))
    trial = next((t for t in trials if t.id == trial_id), None)
    if trial is None:
        raise TrialError("That trial is not on today's scroll")
    day = build_qi_view(store, now)
    return QiCardView(
        choices=qi_choices(trial.qi_expected or 0),
        spent=spent_if(trials, trial_id, check_qi(value)),
        start=day.start,
        redline=day.redline,
    )
