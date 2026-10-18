from collections.abc import Sequence

from scrolly.domain.models import HorizonItem, OriginType, Trial


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
    """Put a trial on top of the Horizon. If its origin is already there, update it instead."""
    key = origin_key(trial)
    kept = [item for item in items if key not in (item.id, item.origin_id)]
    previous = next((item for item in items if key in (item.id, item.origin_id)), None)
    returned = HorizonItem(
        id=previous.id if previous else key,
        title=trial.title,
        is_mandate=trial.is_mandate,
        essence_expected_min=trial.essence_expected_min,
        note=trial.note,
        origin_type=trial.origin_type,
        origin_id=key,
        qi_expected=trial.qi_expected,
    )
    return [returned, *kept]
