import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db.base import Base


@pytest.fixture
def session():
    """テスト用インメモリ SQLite の Session fixture。

    テストごとに独立した DB を用意するため、インメモリ SQLite を使用する。
    - `Base.metadata.create_all()` で全テーブルを作成する
    - `yield` で Session をテスト関数に渡す
    - テスト終了後に Session と engine を破棄する
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        engine.dispose()
