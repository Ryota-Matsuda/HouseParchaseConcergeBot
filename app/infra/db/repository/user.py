
from sqlalchemy.orm import Session

from app.infra.db.models import User
from app.schemas.dto import UserRecord


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, draft: UserRecord) -> User:
        """ユーザーの情報をデータベースに保存する"""
        new_user = User(**draft.model_dump())
        self.session.add(new_user)
        return new_user
