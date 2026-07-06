
from app.infra.db.models import User
from app.infra.db.repository.user import UserRepository
from app.schemas.dto import UserRecord


def test_save(session):
    """新規のユーザーが 保存 されることを確認する"""
    user_repo = UserRepository(session)
    user_record = UserRecord(
        household_id=1,
        name="Test User",
        is_active=True
    )

    user_repo.save(user_record)
    session.commit()

    users_in_db = session.query(User).all()
    assert len(users_in_db) == 1
    assert users_in_db[0].household_id == 1
    assert users_in_db[0].name == "Test User"
    assert users_in_db[0].is_active == True
