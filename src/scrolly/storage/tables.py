from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SettingRow(Base):
    __tablename__ = "setting"
    __table_args__ = (UniqueConstraint("realm_id", "key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    realm_id: Mapped[str] = mapped_column(String(36), default="daily")
    user_id: Mapped[str | None] = mapped_column(String(36), default=None)
    key: Mapped[str] = mapped_column(String(100))
    value_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))


class _Audited:
    """Columns every row carries (CLAUDE.md: UUID id, timestamps, realm, future user)."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    realm_id: Mapped[str] = mapped_column(String(36), default="daily")
    user_id: Mapped[str | None] = mapped_column(String(36), default=None)
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))


class TrialRow(_Audited, Base):
    __tablename__ = "trial"

    logical_day: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(20), index=True)
    is_mandate: Mapped[bool] = mapped_column(Boolean, default=False)
    origin_type: Mapped[str] = mapped_column(String(20))
    origin_id: Mapped[str | None] = mapped_column(String(36), default=None)
    position: Mapped[int] = mapped_column(Integer, default=0)
    essence_expected_min: Mapped[int | None] = mapped_column(Integer, default=None)
    essence_actual_min: Mapped[int | None] = mapped_column(Integer, default=None)
    completed_at: Mapped[str | None] = mapped_column(String(40), default=None)
    note: Mapped[str] = mapped_column(Text, default="")
    timer_started_at: Mapped[str | None] = mapped_column(String(40), default=None)
    timer_paused_at: Mapped[str | None] = mapped_column(String(40), default=None)
    timer_accumulated_s: Mapped[int] = mapped_column(Integer, default=0)
    qi_expected: Mapped[int | None] = mapped_column(Integer, default=None)
    qi_actual: Mapped[int | None] = mapped_column(Integer, default=None)
    art_kind: Mapped[str | None] = mapped_column(String(20), default=None)


class HorizonItemRow(_Audited, Base):
    __tablename__ = "horizon_item"

    title: Mapped[str] = mapped_column(Text)
    is_mandate: Mapped[bool] = mapped_column(Boolean, default=False)
    essence_expected_min: Mapped[int | None] = mapped_column(Integer, default=None)
    note: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    origin_type: Mapped[str] = mapped_column(String(20))
    origin_id: Mapped[str | None] = mapped_column(String(36), default=None)
    qi_expected: Mapped[int | None] = mapped_column(Integer, default=None)
    art_kind: Mapped[str | None] = mapped_column(String(20), default=None)
    worked_s: Mapped[int] = mapped_column(Integer, default=0)


class ArtRow(_Audited, Base):
    __tablename__ = "art"

    kind: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(Text)
    essence_expected_min: Mapped[int | None] = mapped_column(Integer, default=None)
    note: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)
    qi_expected: Mapped[int | None] = mapped_column(Integer, default=None)


class DayRow(_Audited, Base):
    __tablename__ = "day"
    __table_args__ = (UniqueConstraint("realm_id", "logical_day"),)

    logical_day: Mapped[str] = mapped_column(String(10))
    first_sealed_at: Mapped[str | None] = mapped_column(String(40), default=None)
    rolled_over_at: Mapped[str | None] = mapped_column(String(40), default=None)
    dusk_override: Mapped[str | None] = mapped_column(String(20), default=None)
    advisor_silenced: Mapped[bool] = mapped_column(Boolean, default=False)
    qi_start: Mapped[int | None] = mapped_column(Integer, default=None)
    poem_shown_at: Mapped[str | None] = mapped_column(String(40), default=None)
    victory_seen_at: Mapped[str | None] = mapped_column(String(40), default=None)
    planning_started_at: Mapped[str | None] = mapped_column(String(40), default=None)
    planning_accumulated_s: Mapped[int] = mapped_column(Integer, default=0)


class TimerSegmentRow(_Audited, Base):
    __tablename__ = "timer_segment"

    trial_id: Mapped[str] = mapped_column(String(36), index=True)
    discipline: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[str] = mapped_column(String(40))
    ended_at: Mapped[str | None] = mapped_column(String(40), default=None)


class PlanningDraftRow(_Audited, Base):
    __tablename__ = "planning_draft"
    __table_args__ = (UniqueConstraint("realm_id"),)

    logical_day: Mapped[str] = mapped_column(String(10))
    phase: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text, default="")
    qi_start: Mapped[int | None] = mapped_column(Integer, default=None)


class BambooScrapRow(_Audited, Base):
    __tablename__ = "bamboo_scrap"

    opened_at: Mapped[str] = mapped_column(String(40), index=True)
    saved_at: Mapped[str] = mapped_column(String(40))
    closed_at: Mapped[str | None] = mapped_column(String(40), default=None)
    text: Mapped[str] = mapped_column(Text, default="")
    # The trials worked during the visit, in order, as ids joined by commas.
    trial_ids: Mapped[str] = mapped_column(Text, default="")
