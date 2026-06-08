def test_all_models_importable():
    """全データモデルが正しくインポートできるかをテストする"""


def test_all_table_names_are_correct():
    """全データモデルのテーブル名が正しいかをテストする"""
    from app.infra.db.models import (
        Feedback,
        Household,
        Listing,
        MatchResult,
        Notification,
        PreferenceProfile,
        RawListing,
        SearchProfile,
        Source,
        User,
    )

    expected_tables = [
        "households",
        "users",
        "sources",
        "raw_listings",
        "search_profiles",
        "preference_profiles",
        "listings",
        "match_results",
        "notifications",
        "feedbacks",
    ]
    actual_tables = [
        Household.__tablename__,
        User.__tablename__,
        Source.__tablename__,
        RawListing.__tablename__,
        SearchProfile.__tablename__,
        PreferenceProfile.__tablename__,
        Listing.__tablename__,
        MatchResult.__tablename__,
        Notification.__tablename__,
        Feedback.__tablename__,
    ]
    assert actual_tables == expected_tables
