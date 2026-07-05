
from sqlalchemy.orm import Session

from app.infra.db.models import Notification
from app.schemas.dto import NotificationRecord


class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, draft: NotificationRecord) -> Notification:
        """通知の情報をデータベースに保存する"""
        new_notification = Notification(**draft.model_dump())
        self.session.add(new_notification)
        return new_notification
