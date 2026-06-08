# 学習ログ

## 2026-05-16 ~ 2026-05-19 | #7 FastAPIアプリの最小構成

### キー学習
- **APIRouter**: エンドポイントを別ファイルに分離する仕組み
- **設定の遅延読み込み**: モジュールトップで重い処理を呼ばない(テスト時の制御性のため)
- **ヘルスチェックの原則**: 生死だけ返す、設定値などは返さない

### 反省
- 最初はGenspark CrawでAI生成したコードを使ったが、設計判断（main.pyに直書き、/health/settingsの追加）に問題があった
- AIの出力をそのまま使わず、自分でレビューすることの重要性を再確認

### 参考リソース
- FastAPI公式: https://fastapi.tiangolo.com/

## 2026-05-20 ~ 2026-06-01 | #12 データモデルの実装

### キー学習
- **SQLAlchemy 2.0 の Mapped 記法**: `カラム名: Mapped[型] = mapped_column(...)` で Python 側の型ヒントと DB 側のカラム仕様を1行で表現
- **DeclarativeBase**: 全モデルが継承する基底クラス。これを継承することで Python クラスが DB テーブルとして認識される
- **`__tablename__` と `__table_args__`**: 前者はテーブル名指定（必須）、後者は複合 UNIQUE 制約やインデックスなど「テーブル全体に関わる設定」を指定。タプル形式で、要素1つでも末尾カンマ必須
- **ondelete の選択基準**: 「データの自己完結性」と「履歴の必要性」で判断。一貫性のため全 FK を CASCADE で統一し、論理削除（`is_active`）を基本運用とすることで履歴消失リスクを抑える
- **DB型と Python 型ヒントの一致**: `JSON` 型なら `Mapped[dict]`、`Text` 型なら `Mapped[str]`、NULL 許容なら `Mapped[型 | None]`。両者を揃えると IDE 補完が効き読みやすい
- **raw_listings と listings の役割分担**: 前者は生データ保存（HTML をバックアップ）、後者は構造化済みの検索・通知用データ。同じ情報を二重に持たない
- **複合 UNIQUE 制約と timestamp の関係**: `preference_profile` のように内容が変動するエンティティを参照する場合、ID 単位の UNIQUE 制約は不適切。時系列で履歴を持つ方が安全
- **ER 図の表現**: Mermaid 記法は GitHub で自動レンダリングされ、Git で diff が追える。`||--o{` は1対多、`||--||` は1対1、`}o--o{` は多対多
- **pytest の基本**: ファイル名は `test_*.py`、関数名は `test_*`、`assert` 文で検証。1関数1観点が原則

### 反省
- データモデル設計は AI に丸投げせず、たたき台を自分で作って AI にレビューさせる進め方が有効だった。特に「`match_results` の複合 UNIQUE 制約は不要では？」のような気づきは、自分で考えたからこそ生まれた
- 一方で、Mermaid 記法のミスや、`Sources`/`Source` の単複混在、`TEXT`/`Text` の大文字小文字違いなど、機械的なチェックは AI レビューの方が圧倒的に早い。役割分担として「設計判断は自分、表記チェックは AI」が今後の指針
- 「全テーブルに `created_at` を入れる」のような一律ルールを疑い、「外部マスタである `sources` には不要」のようにテーブルの性質で判断する視点が身についた
- AI が提示するコードを全文コピペせず、自分で1行ずつ手入力したことで構文理解が深まった。逆に時間がかかる点は、Issue を分割して30分単位で進めることで継続できた
- テストの粒度では「定義の再記述」を避ける原則を学んだ。カラム一覧の検証テストは不要、振る舞い（importable, テーブル名対応）だけ検証する

### 設計判断メモ
- 全 FK を CASCADE 統一、論理削除（`is_active`）を基本運用とする方針
- `preference_profile` の AI 分析結果カラムは JSON 型で構造化データを保存
- `raw_listings.data` は HTML を Text 型で保存、JSON 化は listings 側で実施
- Enum 化、NOT NULL 制約の細部、スナップショットテーブルなどは Phase D 以降で再検討（ToDo として data-model.md に記録）

### 参考リソース
- SQLAlchemy 2.0 公式: https://docs.sqlalchemy.org/en/20/
- Mermaid ER 図記法: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- pytest 公式: https://docs.pytest.org/

## 2026-06-02 ~ 2026-06-09 | #3 共通ドメインモデルとスキーマの定義

### キー学習
- **Pydantic と SQLAlchemy の責務の違い**: SQLAlchemy はDB永続化（保存形）、Pydantic はアプリ内入出力契約（バリデーション）。同じデータでも「DBに保存する形」と「アプリ内で受け渡す形」は別物
- **DBスキーマとアプリスキーマの差分**: id, created_at, sent_at など「DB側で自動設定する項目」「送信前データには存在しない項目」はアプリスキーマには持たない。逆に line_user_id のように「DBに保存しないが処理に必要な情報」はアプリスキーマだけが持つ
- **BaseModel の基本**: `BaseSettings` の親クラス。`field: 型` で必須、`field: 型 \| None = None` で任意、`Field(..., max_length=N, ge=0)` で制約指定
- **default_factory と default の違い**: `default=datetime.now()` だとクラス定義時の時刻が固定値になる。インスタンス生成時の時刻が欲しければ `default_factory=datetime.now`（関数オブジェクトを渡す）。SQLAlchemy の `mapped_column(default=datetime.now)` と感覚は同じ
- **pytest.raises での例外テスト**: `with pytest.raises(ValidationError):` ブロック内で例外が発生すれば成功。Pydantic のバリデーション動作確認の定型パターン
- **LINE Messaging API の仕組み**: 送信先URLは固定（`api.line.me/...`）、送信先ユーザーは body 内の line_user_id（U で始まる33文字）。Webhook URL は受信側エンドポイントで、送信時には使わない。混同しやすい
- **LINE ユーザーID の取得**: ユーザーが Bot を友だち追加すると LINE が follow イベントを Webhook に POST する。その body から line_user_id を取得して users テーブルに保存しておく

### 反省
- 最初に「URL = LINE の Webhook URL」と誤認していた。Webhook の意味を「受信側エンドポイント」と正しく理解していなかったため。実際の API 仕様を確認する習慣の重要性を再認識
- AI が提示したたたき台に対して、フィールド過不足や設計判断を自分でレビューできた。「シンプルすぎないか」「DBとの整合性」「制約の妥当性」を観点として持てるようになった
- 1スキーマだけ自分で実装し、残り4つを AI に作らせる進め方が機能した。前 Issue の振り返りで決めた「文法を理解したら AI に任せる」を実践できた
- スキーマ実装中に「スコープ外の重要な問題」に気づけた（is_active 更新タイミング、複数ソース同一物件問題）。これを新規 Issue として切り出し、MVP内/MVP後で優先度分けする判断ができた
- テストは「定義の再記述」を避ける原則を継続。1スキーマに対して3観点（正常系、必須欠落、型違反）の3テストで十分という感覚が固まった

### 設計判断メモ
- アプリスキーマは `app/schemas/dto.py` の1ファイルに集約（MVPは分割よりも俯瞰性優先）
- `RawSourceListing.raw_data` は `str` 一本でソース差分を吸収（差分は Normalizer で対応）
- `FilterResult` は DB テーブルを持たない一時データとして扱う。passed_rules / failed_rules を残すことで AI 評価時の文脈情報として使える
- `source_listing_key` は `ListingDraft` で必須に固定。スクレイピング元から取得できない場合は Normalizer が URL ハッシュなど代替キーを生成する責任を持つ
- `priority` の型は MVP では `str`。AI 出力のブレを見て Enum/Literal 化を検討
- docstring にスキーマの役割・フロー・DB との差分を書く運用とした（別ドキュメントは作らない）
- LINE 通知の送信先URLは固定なので `NotificationMessage` には持たない。代わりに line_user_id と listing_url（物件URL）を持つ

### スコープ外として別 Issue 化したもの
- listings.is_active の更新ロジック設計と実装（MVP内）
- 複数ソース間の同一物件検知と重複通知防止（MVP後）
- users テーブルへの line_user_id カラム追加（Phase D の LINE 連携実装時）
- notifications.url の意味を「物件URL」に再定義（data-model.md 更新）

### 参考リソース
- Pydantic 公式: https://docs.pydantic.dev/
- LINE Messaging API: https://developers.line.biz/ja/docs/messaging-api/
- pytest.raises: https://docs.pytest.org/en/stable/how-to/assert.html#assertions-about-expected-exceptions
 