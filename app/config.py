from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

"""アプリの設定クラス。環境変数から読み込む値を定義する。"""
"""必要に応じて、ここにデータベース接続情報や外部APIのキーなども追加していく。"""
"""環境変数から読み込むアプリ設定。
- APP_ENV: 実行環境（local / dev / staging / prod）
- LOG_LEVEL: ログレベル
- DEBUG: デバッグフラグ（APP_ENV から自動算出）
- DATABASE_URL: データベース接続URL
"""


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # アプリ基本情報
    app_name: str = "House Purchase Concierge Bot"
    app_env: Literal["local", "dev", "staging", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    # データベース接続情報
    database_url: str = "sqlite:///./app.db"

    @property
    def debug(self) -> bool:
        """local / dev のみデバッグモード扱い。"""
        return self.app_env in ("local", "dev")


"""アプリの設定はアプリで1つだけで十分なので、シングルトンとしてキャッシュする。"""


@lru_cache
def get_settings() -> Settings:
    """設定インスタンスを取得する（キャッシュ済み）。"""
    return Settings()
