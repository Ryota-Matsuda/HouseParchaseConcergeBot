"""FastAPI アプリのエントリーポイント。

ローカル起動:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/health")
def health() -> dict[str, str]:
    """ヘルスチェック用エンドポイント。

    監視や疎通確認で利用される。
    """
    return {"status": "ok", "env": settings.app_env}
