from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """ヘルスチェック用エンドポイント。

    監視や疎通確認で利用される。
    """
    settings = get_settings()
    return {"status": "ok", "env": settings.app_env}
