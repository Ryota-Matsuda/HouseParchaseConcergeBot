from app.infra.db.models import SearchProfile
from app.infra.db.repository.search_profile import SearchProfileRepository


def test_find_active_returns_only_active_profiles_for_given_household(session):
    """Household_idに該当するActiveなSearchProfileが取得できることを確認する"""
    searchprofile_repo = SearchProfileRepository(session)
    inactiveprofile = SearchProfile(
        id=1,
        household_id=1,
        is_active=False,
    )
    session.add(inactiveprofile)
    activeprofile = SearchProfile(
        id=2,
        household_id=2,
        is_active=True,
    )
    session.add(activeprofile)
    another_activeprofile = SearchProfile(
        id=3,
        household_id=3,
        is_active=True,
    )
    session.add(another_activeprofile)
    session.commit()

    active_search_profiles = searchprofile_repo.find_active(household_id=2)
    assert len(active_search_profiles) == 1
    assert active_search_profiles[0].id == 2
