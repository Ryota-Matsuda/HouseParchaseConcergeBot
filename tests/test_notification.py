from datetime import datetime

from app.infra.db.models import Notification
from app.infra.db.repository.notification import NotificationRepository
from app.schemas.dto import NotificationRecord


def test_save(session):
    """新規の通知が保存されることを確認する"""
    notification_repo = NotificationRepository(session)
    notification_draft = NotificationRecord(
        match_result_id=1,
        user_id=1,
        url="http://example.com/test-listing",
        contents="Test notification content",
        sent_at=datetime.now(),
        sent_status="success",
        error_message=None,
    )

    notification_repo.save(notification_draft)
    session.commit()

    notifications_in_db = session.query(Notification).all()
    assert len(notifications_in_db) == 1
    assert notifications_in_db[0].user_id == 1
