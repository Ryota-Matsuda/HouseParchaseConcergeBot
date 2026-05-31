from datetime import datetime

from sqlalchemy import Text, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    # 同じ世帯で同じ名前のユーザーは存在できない複合制約
    __table_args__ = (UniqueConstraint("household_id", "name", name="uq_user_household_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ToDo:将来Enum化を検討
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class RawListing(Base):
    __tablename__ = "raw_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    # ToDo:ondeleteの処理は変更の可能性あり。
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    data: Mapped[str] = mapped_column(Text, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
