from datetime import datetime

from sqlalchemy.orm import Session

from app.infra.db.models import Listing
from app.schemas.dto import ListingDraft


class ListingRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, draft: ListingDraft) -> Listing:
        # 既存を探す。DBの複合ユニーク制約に基づき、source_idとsource_listing_keyで検索
        existing = (
            self.session.query(Listing)
            .filter_by(
                source_id=draft.source_id,
                source_listing_key=draft.source_listing_key,
            )
            .first()
        )

        if existing:
            # 既存があれば全フィールドを更新
            for key, value in draft.model_dump().items():
                setattr(existing, key, value)
            existing.normalized_at = datetime.now()
            existing.last_seen_at = datetime.now()
            existing.is_active = True
            return existing
        else:
            # なければ新規追加
            new_listing = Listing(**draft.model_dump())
            new_listing.normalized_at = datetime.now()
            new_listing.last_seen_at = datetime.now()
            new_listing.is_active = True
            self.session.add(new_listing)
            return new_listing
