from sqlalchemy.orm import Session

from app.infra.db.models import SearchProfile


class SearchProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_active(self, household_id: int) -> list[SearchProfile]:
        return (
            self.session.query(SearchProfile)
            .filter_by(is_active=True, household_id=household_id)
            .all()
        )
