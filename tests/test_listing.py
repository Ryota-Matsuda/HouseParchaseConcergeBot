from app.infra.db.models import Listing
from app.infra.db.repository.listing import ListingRepository
from app.schemas.dto import ListingDraft


def test_upsert_insert(session):
    """新規のリスティングが INSERT されることを確認する"""
    listing_repo = ListingRepository(session)
    listing_draft = ListingDraft(
        raw_listing_id=1,
        source_id=1,
        source_listing_key="test_key",
        title="Test Listing",
        url="http://example.com/test-listing",
    )

    listing_repo.upsert(listing_draft)
    session.commit()

    listings_in_db = session.query(Listing).all()
    assert len(listings_in_db) == 1
    assert listings_in_db[0].source_listing_key == "test_key"


def test_upsert_update(session):
    """既存のリスティングが UPDATE され、件数が増えないことを確認する"""
    listing_repo = ListingRepository(session)

    # 初期データを投入
    initial_draft = ListingDraft(
        raw_listing_id=1,
        source_id=1,
        source_listing_key="test_key",
        title="Initial Listing",
        url="http://example.com/initial-listing",
    )
    listing_repo.upsert(initial_draft)
    session.commit()

    # 同じキーで更新
    updated_draft = ListingDraft(
        raw_listing_id=2,
        source_id=1,
        source_listing_key="test_key",
        title="Updated Listing",
        url="http://example.com/updated-listing",
    )
    listing_repo.upsert(updated_draft)
    session.commit()

    listings_in_db = session.query(Listing).all()
    assert len(listings_in_db) == 1
    assert listings_in_db[0].title == "Updated Listing"
