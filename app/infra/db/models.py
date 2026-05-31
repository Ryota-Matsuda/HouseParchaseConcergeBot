from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
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
    url: Mapped[str] = mapped_column(Text, nullable=False)
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


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False
    )
    area_name: Mapped[str | None] = mapped_column(String(100))
    station_name: Mapped[str | None] = mapped_column(String(100))
    walk_minutes_max: Mapped[int | None] = mapped_column()
    price_min: Mapped[int | None] = mapped_column()
    price_max: Mapped[int | None] = mapped_column()
    construction_year_min: Mapped[int | None] = mapped_column()
    construction_year_max: Mapped[int | None] = mapped_column()
    layout: Mapped[str | None] = mapped_column(String(50))
    floor_space_min: Mapped[int | None] = mapped_column()
    # ToDo:将来Enum化を検討(マンション/戸建て/注文住宅)
    property_type: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class PreferenceProfile(Base):
    __tablename__ = "preference_profiles"

    # 同じユーザーに対して複数のPreferenceProfileが存在できないようにするUNIQUE制約
    __table_args__ = (UniqueConstraint("user_id", name="uq_preference_profile_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    preference_area: Mapped[str | None] = mapped_column(String(100))
    important_condition: Mapped[dict | None] = mapped_column(JSON)
    prevent_condition: Mapped[dict | None] = mapped_column(JSON)
    feedback_trend: Mapped[dict | None] = mapped_column(JSON)


class Listing(Base):
    __tablename__ = "listings"

    # 同じソース内で同じ物件IDを重複登録しない複合UNIQUE制約
    __table_args__ = (
        UniqueConstraint("source_id", "source_listing_key", name="uq_listing_source_key"),
    )

    # 1つのRawListingに対して1つのListingが存在する前提で、RawListingのIDを外部キーとして持つ。
    id: Mapped[int] = mapped_column(primary_key=True)
    raw_listing_id: Mapped[int] = mapped_column(
        ForeignKey("raw_listings.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    source_listing_key: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    area_name: Mapped[str | None] = mapped_column(String(100))
    station_name: Mapped[str | None] = mapped_column(String(100))
    walk_minutes: Mapped[int | None] = mapped_column()
    price: Mapped[int | None] = mapped_column()
    construction_year: Mapped[int | None] = mapped_column()
    layout: Mapped[str | None] = mapped_column(String(50))
    floor_space: Mapped[int | None] = mapped_column()
    # ToDo:将来Enum化を検討(マンション/戸建て/注文住宅)
    property_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    normalized_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
