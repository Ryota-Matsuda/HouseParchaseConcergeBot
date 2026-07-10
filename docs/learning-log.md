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

## 2026-06-09 – 2026-06-20 | #9 Alembic 初期マイグレーション作成

**キー学習**
- Alembic は SQLAlchemy の公式マイグレーションツールだが、技術的には別パッケージ。`pip install alembic` が別途必要で、pyproject.toml にも別依存として追加する。
- SQLAlchemy はアプリ実行中の DB 操作（読み書き、SQL生成）を担当し、Alembic はスキーマ変更の履歴管理と適用を担当する。役割が時間軸で分かれている。
- マイグレーションファイルは `upgrade()` と `downgrade()` のペアで構成され、revision と down_revision の連鎖で履歴チェーンを形成する（Git の commit と parent の関係に近い）。
- `alembic init alembic` で `alembic.ini` と `alembic/` ディレクトリ（env.py, script.py.mako, versions/）が生成される。配置はプロジェクトルートが慣習で、`app/` 配下には置かない（アプリではなく開発ツールだから）。
- env.py の改修ポイント2つ：`target_metadata = Base.metadata` でモデル定義を Alembic に教える、`config.set_main_option("sqlalchemy.url", ...)` で alembic.ini の DB URL を上書きする。
- env.py と config.py は別プロセスで動くため両方が DB URL を知る必要があるが、二重管理を避けるため env.py から `get_settings()` を呼ぶ構成にする（Single Source of Truth）。
- `alembic revision --autogenerate -m "..."` で models.py と DB の差分から migration ファイルを自動生成。ただし autogenerate は完璧ではなく、カラム名変更などは「削除＋追加」と誤検出する可能性があるため、生成ファイルの目視確認が鉄則。
- 主要コマンド：`upgrade head`（最新まで適用）、`downgrade base`（全て戻す）、`downgrade -1`（1つ戻す）、`current`（現在のリビジョン）、`history`（履歴一覧）。
- SQLite の DB ファイルは `alembic upgrade` の実行時に自動生成される。PostgreSQL/MySQL のように事前に空 DB を作る必要はない。
- `alembic_version` という Alembic 内部管理テーブルが DB に作られ、downgrade base しても残る。完全リセットには `app.db` ファイル削除が必要。
- `ondelete` を省略した外部キーは「RESTRICT」相当の挙動になり、親削除を阻止する。「親削除して子は残したい」場合は `ondelete="SET NULL"` + `nullable=True` + 型を `int | None` の3点セットが必要。

**反省**
- 設計判断（users の ondelete を SET NULL にする）の副作用に自分で気づけた。「household 離脱後の user の search_profile 参照問題」を発見し、即 Issue 化してスコープを守れた。
- env.py の改修で最初に `get_main_option(key, default)` のデフォルト引数で対応しようとしたが、これは alembic.ini にプレースホルダが残っているため効かないことを学んだ。`set_main_option` で上書きするのが正攻法。
- ruff/black の指摘を「自動生成ファイルだから除外設定」という判断ができた。ツールに従うか、ツールを設定するかの境界感覚が身についた。
- 「自分で実装 → AI レビュー」の方針は、初めて触るツール（Alembic）でも有効だった。完全に AI に任せると env.py の役割や set_main_option の意味を理解できないまま進んでいた可能性が高い。
- Phase A、B の整理を md にアウトプットする習慣が定着し、4日空いても再開がスムーズだった。

**設計判断メモ**
- Alembic 関連ファイルはプロジェクトルートに配置（`alembic.ini` と `alembic/` ディレクトリ）。Alembic は開発ツールなので `app/` 配下には入れない。
- DB URL は `app/config.py` の `Settings.database_url` で管理し、env.py から `get_settings()` を呼んで `set_main_option` で alembic.ini を上書きする。alembic.ini の `sqlalchemy.url` は触らず、デフォルトのプレースホルダのまま残す。
- `users.household_id` は `ondelete="SET NULL"` + `nullable=True` + `Mapped[int | None]` の3点セットで「household 削除後も user を残す」設計を採用。他のテーブルは CASCADE で統一。
- `alembic/versions/` 配下は ruff と black の対象外に設定（`pyproject.toml` の `extend-exclude`）。理由は自動生成ファイルだから。`alembic/env.py` は対象に残す（自分で編集するから）。
- マイグレーションファイルは Git で管理（`.gitignore` に追加しない）。逆に `*.db` は除外（バイナリでチーム共有不要）。
- スキーマ変更時の運用は「models.py 修正 → autogenerate → ファイル目視確認 → upgrade head」の4ステップで統一。README に明文化。

**スコープ外・別 Issue 化**
- アプリ起動時に「DB が最新マイグレーションに追いついているか」を自動チェックする仕組み（既に Issue 起票済、MVP 後）
- household 離脱後の user の search_profile 参照ロジック検討（今回新規発見、別 Issue 起票予定）
- プロジェクト名の表記揺れ整理（README、リポジトリ名、pyproject.toml の name で微妙にスペルが違う、MVP 後の整理対象）

**参考リソース**
- Alembic 公式: https://alembic.sqlalchemy.org/
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- SQLAlchemy ondelete: https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.ForeignKey.params.ondelete

#9 の学習は、Alembic 単体の使い方だけでなく「開発ツールの設定と責任の境界」「設定の Single Source of Truth」「設計判断の副作用への気づき」など、データベース運用全般のスキルに繋がった。特に「ondelete の挙動」と「自動生成ファイルとの付き合い方」は今後のプロジェクトでも繰り返し出会うパターン。Issue #9 完走、お疲れさまでした！

## 2026-06-22 ~ 2026-07-10 | #5 Repository層の実装

### キー学習
- **Repository パターンの本質**: 「永続化ストレージへの操作を1つの窓口にまとめる」こと。読み書き両方を持つ必要はなく、読み取り専用の Repository も普通に存在する（例: SearchProfileRepository）
- **モデル定義と Repository の恩恵は独立**: モデル定義は「SQLAlchemy 構文が使える」、Repository は「SQLAlchemy 構文さえ書かずに済む」。両方あって初めてアプリ層が DB を意識しない設計になる
- **Session の Unit of Work パターン**: Session は「管理下のオブジェクトの変更を全て記憶する」仕組み。`session.add()` した新規、`session.query()` 後にフィールドを書き換えたオブジェクト、`session.delete()` した削除対象を全て内部で追跡。`session.commit()` 時に一括で SQL に変換して発行するため、commit に引数は不要
- **engine / Session / sessionmaker の役割分担**: engine は接続プール（アプリ全体で1つ）、Session は対話単位（トランザクション境界）、sessionmaker は Session を作る工場。分離することで並列処理とテスタビリティを両立
- **Session はコンストラクタ注入（DI）**: Repository 内で作らない理由は、複数 Repository が同一 Session を共有できること、テスト用と本番用で差し替え可能にすること
- **commit は呼び出し側の責務**: Repository は commit しない。理由は「複数 Repository をまたぐトランザクション」を業務単位で扱うため。commit のタイミング決定は業務判断であり、Repository の責務ではない
- **Repository は「型変換 + 保存」に純粋化**: 情報追加（`sent_at` の生成、`sent_status` の判定など）は前段のモジュール（Notifier など）が確定させて Record として渡す。Repository が業務ロジックを持つと責務が混濁する
- **pytest fixture の仕組み**: `@pytest.fixture` でデコレートし、テスト関数の引数名と一致すると自動注入される。`yield` までが前準備、以降がクリーンアップ。`conftest.py` に置くと同ディレクトリ以下から名前だけで参照可能
- **インメモリ SQLite でのテスト**: `sqlite:///:memory:` + function スコープ fixture + `Base.metadata.create_all()` で、各テストが独立した DB を持つ。高速、独立性、本番影響なしの3つを同時に達成
- **`try/finally` によるリソース保証**: assert 失敗や例外が起きても close と dispose が確実に走る。「リソース確保と解放はセット」という Python の鉄則
- **DTO とモデルを分ける理由**: (1) 変更容易性（片方の変更が他方に波及しない）、(2) テスタビリティ（Pydantic は engine 不要でインスタンス化可能）、(3) API 連携（FastAPI で入出力型として再利用可能）、(4) 依存方向の一貫性維持

### 反省
- 「モデルがあれば SQLAlchemy が使える／Repository があれば SQLAlchemy 構文すら書かずに済む」という抽象化の階層に気づいた瞬間が今回の最大の学びだった。それまで Repository の恩恵が Phase A の記述と矛盾して見えていた
- 「Repository が commit を呼ばない理由」の理解に一番時間がかかった。複数 Repository をまたぐトランザクションを想像できるようになって初めて腑に落ちた
- NotificationRepository 実装時に「引数の型は何がふさわしいか」を自分で違和感として言語化できた。この違和感が `NotificationRecord` DTO 新設という設計判断につながった。違和感の言語化＝設計判断の入り口
- pytest fixture の仕組みを1度理解した後も土日を挟むと薄れる。復習の必要性を実感し、セルフチェック用の自問リストを毎回残す運用を確立
- AI Developer の使い方の方針を明確化：初めて触る技術や設計判断は自分で書く、繰り返しパターン部分は AI に任せてレビューに集中。「レビュー力は書く経験から育つ」を実感
- テストの assertion 粒度が Repository ごとにばらついた。次回以降は「保存された」だけでなく「正しい値で保存された」を全 Repository で揃える
- Phase A/B/C の3段階（要件整理→技術理解→実装）が定着し、間が空いても復習で戻れるようになった

### 設計判断メモ
- Repository は Repository ごとにファイル分割（`app/infra/db/repository/listing.py` など）。1ファイル集約案は却下、責務ごとの分離を優先
- 全 Repository で `__init__(self, session: Session)` を統一。DI と一貫性のため
- 「DB 保存用 DTO」を新設する方針を確立：`NotificationRecord`, `FeedbackRecord`, `UserRecord`。既存の `NotificationMessage`（送信用）と役割を分離し、フィールドの時系列的な意味を明確化
- SearchProfileRepository は読み取り専用（`find_active` のみ）。`save` は「ユーザーが検索条件を設定する Issue」で追加。YAGNI 適用
- UserRepository は `save` のみ。`find_by_line_id` などは LINE 連携 Issue で追加
- テストはインメモリ SQLite + function スコープ fixture。テストデータは Repository の `save` メソッド経由か、`session.add()` 直接投入のどちらも許容（テストコードでは規約を緩める）
- `alembic/versions/` は ruff/black の除外（前 Issue で決定）。Repository/テストコードは対象

### スコープ外・別 Issue 化
- User モデルへの `line_user_id` カラム追加（LINE 連携の前提として必要、要新規起票）
- LINE Webhook 受信基盤（FastAPI + 署名検証、要新規起票）
- LINE 友だち追加時のユーザー登録フロー（要新規起票）
- Household 作成・参加フロー（要新規起票、`HouseholdRepository.save` も同時実装）
- SearchProfile 設定フロー（要新規起票、`SearchProfileRepository.save` も同時実装）
- Feedback 受信フロー（要新規起票、MVP+ の可能性あり）
- テストの assertion 粒度統一（次回意識するレベル、Issue 化不要）

### 参考リソース
- SQLAlchemy Session and Unit of Work: https://docs.sqlalchemy.org/en/20/orm/session.html
- pytest fixture: https://docs.pytest.org/en/stable/how-to/fixtures.html
- Pydantic v2: https://docs.pydantic.dev/latest/

#5 の学習は、Repository パターン単体だけでなく「モジュール間の責務分離」「DTO 設計の時系列的な意味付け」「Unit of Work パターン」など、アプリ全体の設計思想に繋がった。特に「Repository は型変換に純粋化、業務ロジックは呼び出し側」の原則は、今後 Notifier や FeedbackHandler を実装するときも同じ思考パターンで進められる。Issue #5 完走、お疲れさまでした！
