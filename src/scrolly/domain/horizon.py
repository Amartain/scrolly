from collections.abc import Sequence
from dataclasses import replace

from scrolly.domain.duration import parse_duration
from scrolly.domain.models import ArtKind, HorizonItem, OriginType, Trial


def same_title(left: str, right: str) -> bool:
    """Horizon duplicates ignore case and surrounding spaces."""
    return left.strip().casefold() == right.strip().casefold()


def has_title(items: Sequence[HorizonItem], title: str) -> bool:
    return any(same_title(item.title, title) for item in items)


def origin_key(trial: Trial) -> str:
    """The identity a trial carries back to the Horizon."""
    if trial.origin_type is OriginType.HORIZON and trial.origin_id:
        return trial.origin_id
    return trial.id


def return_to_horizon(items: Sequence[HorizonItem], trial: Trial) -> list[HorizonItem]:
    """Put a trial on top of the Horizon. If its origin is already there, update it instead.

    The time worked goes with it (a running timer must be paused first).
    An Art instance carries none.
    """
    key = origin_key(trial)
    kept = [item for item in items if key not in (item.id, item.origin_id)]
    previous = next((item for item in items if key in (item.id, item.origin_id)), None)
    earlier = previous.worked_s if previous else 0
    worked = 0 if trial.art_kind else trial.timer_accumulated_s + earlier
    returned = HorizonItem(
        id=previous.id if previous else key,
        title=trial.title,
        is_mandate=trial.is_mandate,
        essence_expected_min=trial.essence_expected_min,
        note=trial.note,
        origin_type=trial.origin_type,
        origin_id=key,
        qi_expected=trial.qi_expected,
        art_kind=trial.art_kind,
        worked_s=worked,
    )
    return [returned, *kept]


class HorizonError(ValueError):
    """A change to the Horizon that cannot be made. The message is shown to the user."""


def _title(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise HorizonError("A trial needs a title")
    return cleaned


def add_item(
    items: Sequence[HorizonItem],
    item_id: str,
    title: str,
    estimate: str = "",
    art_kind: ArtKind | None = None,
) -> list[HorizonItem]:
    """A new idea goes on top of the Horizon. A blank estimate means none."""
    item = HorizonItem(
        id=item_id,
        title=_title(title),
        essence_expected_min=parse_duration(estimate),
        art_kind=art_kind,
    )
    return [item, *items]


def edit_item(
    items: Sequence[HorizonItem],
    item_id: str,
    title: str | None = None,
    estimate: str | None = None,
    is_mandate: bool | None = None,
) -> list[HorizonItem]:
    """Change the title, estimate and/or type of one item. A blank estimate clears it."""
    target = next((item for item in items if item.id == item_id), None)
    if target is None:
        raise HorizonError("That item is no longer on the Horizon")
    if is_mandate and target.art_kind is not None:
        raise HorizonError("Arts cannot be Heavenly Mandates")
    return [
        replace(
            item,
            title=item.title if title is None else _title(title),
            essence_expected_min=(
                item.essence_expected_min if estimate is None else parse_duration(estimate)
            ),
            is_mandate=item.is_mandate if is_mandate is None else is_mandate,
        )
        if item.id == item_id
        else item
        for item in items
    ]


def remove_item(items: Sequence[HorizonItem], item_id: str) -> list[HorizonItem]:
    if not any(item.id == item_id for item in items):
        raise HorizonError("That item is no longer on the Horizon")
    return [item for item in items if item.id != item_id]
