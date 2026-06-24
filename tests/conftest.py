import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.models import Base


@pytest.fixture(scope="function")
def session():
    """
    テストデータ用のインメモリSQLiteデータベースを作成
    """
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
