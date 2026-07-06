from datetime import datetime

from app.infra.db.models import Feedback
from app.infra.db.repository.feedback import FeedbackRepository
from app.schemas.dto import FeedbackRecord


def test_save(session):
    """新規のフィードバックが 保存 されることを確認する"""
    feedback_repo = FeedbackRepository(session)
    feedback_record = FeedbackRecord(
        user_id=1,
        notification_id=1,
        feedback_type="feedback_type_example",
        feedback_detail="Test feedback detail",
        has_registered=True,
        responded_at=datetime.now(),
    )

    feedback_repo.save(feedback_record)
    session.commit()

    feedbacks_in_db = session.query(Feedback).all()
    assert len(feedbacks_in_db) == 1
    assert feedbacks_in_db[0].user_id == 1
    assert feedbacks_in_db[0].notification_id == 1
    assert feedbacks_in_db[0].feedback_type == "feedback_type_example"
    assert feedbacks_in_db[0].feedback_detail == "Test feedback detail"
    assert feedbacks_in_db[0].has_registered == True
