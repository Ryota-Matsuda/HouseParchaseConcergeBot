from datetime import datetime

from pydantic import BaseModel, Field


class NotificationMessage(BaseModel):
    """Notification message スキーマ
    LINE通知の入力データ

    AISourceResultからNotificationCreatorが生成する。
    Notifierに渡され、notificationsテーブルに保存される。

    DBとの差分：
    id,match_result_id,sent_at,sent_statusはNotifierが生成するため、ここには含まれない。

    フロー：
    AIScoreResult → NotificationCreator → NotificationMessage
    """

    user_id: int = Field(..., description="DB上のユーザID")
    line_user_id: str = Field(..., max_length=100, description="通知先のLINEユーザID")
    listing_url: str = Field(..., max_length=500, description="物件情報URL")
    contents: str = Field(..., max_length=5000, description="通知内容")


class NotificationRecord(BaseModel):
    """Notification record スキーマ
    notificationの結果と送信メッセージの情報をまとめたスキーマ。

    DBとの差分：
    - idはDB側で自動設定されるため不要

    フロー：
    NotificationMessage → Notifier → NotificationRecord → Repository → notifications
    """

    match_result_id: int = Field(..., description="DB上の評価結果ID")
    user_id: int = Field(..., description="DB上のユーザID")
    url: str | None = Field(None, max_length=500, description="物件情報URL")
    contents: str | None = Field(None, max_length=5000, description="通知内容")
    sent_at: datetime = Field(..., description="送信日時")
    sent_status: str | None = Field(None, max_length=50, description="送信ステータス")
    error_message: str | None = Field(None, description="送信エラー時のメッセージ")


class FeedbackRecord(BaseModel):
    """Feedback record スキーマ
    feedbackの結果と送信メッセージの情報をまとめたスキーマ。

    DBとの差分：
    - idはDB側で自動設定されるため不要

    フロー：
    LINE Webhook (通知への返信) → FeedbackHandler → FeedbackRecord → Repository → feedbacks

    """

    user_id: int = Field(..., description="DB上のユーザID")
    notification_id: int = Field(..., description="DB上の通知ID")
    # ToDo:将来Enum化を検討(気になる/いまいち/後で見る)
    feedback_type: str | None = Field(None, max_length=50, description="フィードバック種別")
    feedback_detail: str | None = Field(None, description="フィードバック詳細")
    has_registered: bool = Field(..., description="PreferenceProfileに登録済みかどうかのフラグ")
    responded_at: datetime = Field(..., description="フィードバック送信日時")


class UserRecord(BaseModel):
    """User record スキーマ
    ユーザーの情報をまとめたスキーマ。LINEの友達追加時に使う

    DBとの差分：
    - idはDB側で自動設定されるため不要

    フロー：
    UserRecord → Repository → users
    """

    household_id: int | None = Field(None, description="DB上の世帯ID")
    name: str = Field(..., max_length=100, description="ユーザー名")
    is_active: bool = Field(True, description="ユーザーがアクティブかどうかのフラグ")


class RawSourceListing(BaseModel):
    """ソースから取得した生データを表すスキーマ。

    WebScraper が取得した直後のデータ。
    まだ正規化されていないため、ソース固有のフォーマット（HTML等）を保持する。
    DBの raw_listings テーブルへの登録元になる。

    DBとの差分:
    - id, fetched_at は DB 側で自動設定するため不要
    - source_id は事前に解決済みである前提

    フロー:
    Source → WebScraper → RawSourceListing → Repository → raw_listings
    """

    source_id: int = Field(..., description="DB上のソースID")
    source_listing_key: str | None = Field(
        None, max_length=100, description="ソースサイト内での物件ID"
    )
    raw_data: str = Field(..., description="取得した生データ（HTML文字列等）")


class ListingDraft(BaseModel):
    """正規化済みの物件データを表すスキーマ。

    Normalizer が RawSourceListing を解析・正規化した結果。
    DB の listings テーブルへの登録元になる。

    DBとの差分:
    - id, normalized_at, is_active, last_seen_at は DB 側で自動設定
    - raw_listing_id, source_id は事前に解決済みである前提

    フロー:
    RawSourceListing → Normalizer → ListingDraft → Repository → listings
    """

    raw_listing_id: int = Field(..., description="元となる生データID")
    source_id: int = Field(..., description="DB上のソースID")
    source_listing_key: str = Field(
        ...,
        max_length=100,
        description="ソースサイト内での物件ID(ない場合はNormalizerが生成するURLのハッシュ値)",
    )
    title: str = Field(..., max_length=500, description="物件タイトル")
    url: str = Field(..., max_length=500, description="物件詳細ページURL")
    # 以下はソースによって取得できないこともあるため任意
    area_name: str | None = Field(None, max_length=100, description="エリア名")
    station_name: str | None = Field(None, max_length=100, description="最寄り駅")
    walk_minutes: int | None = Field(None, ge=0, description="駅徒歩時間（分）")
    price: int | None = Field(None, ge=0, description="価格")
    construction_year: int | None = Field(None, ge=0, description="築年数")
    layout: str | None = Field(None, max_length=50, description="間取り")
    floor_space: int | None = Field(None, ge=0, description="床面積")
    # ToDo: AIの分析がぶれる場合は、Enum化を検討（マンション/戸建て/注文住宅）
    property_type: str | None = Field(None, max_length=50, description="物件種別")
    description: str | None = Field(None, description="物件説明")


class FilterResult(BaseModel):
    """RuleEngine による条件フィルタの判定結果スキーマ。

    各 listing が search_profile の条件を満たすかを判定した結果。
    通過した listing のみが AIAnalyzer に渡される。

    DBとの差分:
    - DBに直接対応するテーブルはない（ログ用または一時データ）

    フロー:
    listings + search_profile → RuleEngine → FilterResult
    FilterResult.passed=True のものだけ → AIAnalyzer
    """

    listing_id: int = Field(..., description="判定対象の物件ID")
    search_profile_id: int = Field(..., description="判定に使った検索条件ID")
    passed: bool = Field(..., description="フィルタを通過したか")
    passed_rules: list[str] = Field(default_factory=list, description="通過したルール名一覧")
    failed_rules: list[str] = Field(
        default_factory=list, description="不通過の理由となったルール名一覧"
    )
    evaluated_at: datetime = Field(default_factory=datetime.now, description="判定日時")


class AIScoreResult(BaseModel):
    """AI による物件評価結果スキーマ。

    AIAnalyzer が FilterResult を通過した物件を評価した結果。
    DB の match_results テーブルへの登録元になる。

    DBとの差分:
    - id, evaluated_at は DB 側で自動設定
    - listing_id, search_profile_id, preference_profile_id は事前に解決済み

    フロー:
    FilterResult(passed) + listings + preference_profile
    → AIAnalyzer → AIScoreResult → Repository → match_results
    """

    listing_id: int = Field(..., description="評価対象の物件ID")
    search_profile_id: int = Field(..., description="使用した検索条件ID")
    preference_profile_id: int = Field(..., description="使用したユーザ嗜好ID")
    ai_description: str | None = Field(None, description="AI要約")
    # ToDo: AIからの回答がぶれる場合は、Enum化を検討（high/medium/low など）
    priority: str | None = Field(None, max_length=50, description="優先度スコア")
    recommend_reason: str | None = Field(None, description="おすすめ理由")
    evidence: str | None = Field(None, description="根拠データ")
