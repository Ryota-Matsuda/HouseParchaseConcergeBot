from sqlalchemy.orm import Session

from app.infra.db.models import Feedback
from app.schemas.dto import FeedbackRecord


class FeedbackRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, draft: FeedbackRecord) -> Feedback:
        """フィードバックの情報をデータベースに保存する"""
        new_feedback = Feedback(**draft.model_dump())
        self.session.add(new_feedback)
        return new_feedback
