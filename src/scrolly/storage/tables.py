from sqlalchemy import String, Text, UniqueConstraint
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
