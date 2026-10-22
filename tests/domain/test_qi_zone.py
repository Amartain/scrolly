import pytest

from scrolly.domain.qi import QiZone, qi_zone


@pytest.mark.parametrize(
    ("value", "zone"),
    [
        (0, QiZone.HARMONIOUS),
        (100, QiZone.HARMONIOUS),
        (101, QiZone.IGNITING),
        (130, QiZone.IGNITING),
        (131, QiZone.STRAIN),
        (500, QiZone.STRAIN),
    ],
)
def test_the_zone_follows_the_day_start_then_the_igniting_stretch(value: int, zone: QiZone) -> None:
    assert qi_zone(value, start=100) is zone


def test_a_lower_start_moves_every_zone_down() -> None:
    assert qi_zone(80, start=70) is QiZone.IGNITING
