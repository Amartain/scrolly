"""Which Art, if any, a title names. A title that matches an Art makes an instance of it. Pure."""

from collections.abc import Sequence
from dataclasses import replace

from scrolly.domain.horizon import same_title
from scrolly.domain.models import Art, ArtKind, HorizonItem, OriginType, Trial


def art_kind_for(title: str, arts: Sequence[Art]) -> ArtKind | None:
    """The kind of the Art this title names (trimmed, case-insensitive), Foundational first."""
    for kind in ArtKind:
        if any(a.kind is kind and same_title(a.title, title) for a in arts):
            return kind
    return None


def with_title[Item: (Trial, HorizonItem)](item: Item, title: str, arts: Sequence[Art]) -> Item:
    """The item under a new title. An Art instance is never a Mandate, so a match drops it."""
    kind = art_kind_for(title, arts)
    return replace(item, title=title, art_kind=kind, is_mandate=item.is_mandate and kind is None)


def kind_of_origin(origin: OriginType) -> ArtKind | None:
    """For importers: a row that came from an Art list is an instance of that kind."""
    if origin is OriginType.FOUNDATIONAL_ART:
        return ArtKind.FOUNDATIONAL
    if origin is OriginType.RESTORATIVE_ART:
        return ArtKind.RESTORATIVE
    return None
