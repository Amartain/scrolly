from scrolly.domain.art_match import art_kind_for, kind_of_origin, with_title
from scrolly.domain.models import Art, ArtKind, OriginType
from tests.factories import make_item, make_trial

ARTS = [
    Art(id="f1", kind=ArtKind.FOUNDATIONAL, title="Carry Water"),
    Art(id="r1", kind=ArtKind.RESTORATIVE, title="Nap"),
    Art(id="r2", kind=ArtKind.RESTORATIVE, title="Carry Water"),
]


def test_a_title_matches_an_art_ignoring_case_and_spaces() -> None:
    assert art_kind_for("  carry WATER ", ARTS) is ArtKind.FOUNDATIONAL
    assert art_kind_for("nap", ARTS) is ArtKind.RESTORATIVE


def test_a_name_in_both_lists_counts_as_foundational() -> None:
    assert art_kind_for("Carry Water", list(reversed(ARTS))) is ArtKind.FOUNDATIONAL


def test_other_titles_match_nothing() -> None:
    assert art_kind_for("Carry Water, the Fifth Trip", ARTS) is None
    assert art_kind_for("Anything", []) is None


def test_renaming_to_an_art_title_makes_an_instance_and_drops_the_mandate() -> None:
    mandate = make_trial("Taxes", is_mandate=True)
    renamed = with_title(mandate, "Nap", ARTS)
    assert (renamed.title, renamed.art_kind, renamed.is_mandate) == (
        "Nap",
        ArtKind.RESTORATIVE,
        False,
    )


def test_renaming_away_from_an_art_title_makes_a_plain_trial() -> None:
    instance = make_item("Nap", art_kind=ArtKind.RESTORATIVE)
    renamed = with_title(instance, "Siesta", ARTS)
    assert renamed.art_kind is None


def test_the_origin_of_an_imported_art_gives_its_kind() -> None:
    assert kind_of_origin(OriginType.FOUNDATIONAL_ART) is ArtKind.FOUNDATIONAL
    assert kind_of_origin(OriginType.RESTORATIVE_ART) is ArtKind.RESTORATIVE
    assert kind_of_origin(OriginType.HORIZON) is None
