# House Purchase Concierge Bot

住宅購入をサポートするコンシェルジュBot。

## 必要環境

- Python 3.12 以上
- Git
- PowerShell（Windows の場合）

---

## 初回セットアップ手順

リポジトリをクローンしたあと、以下の手順でローカル開発環境を構築します。

### 1. リポジトリのルートに移動

```powershell
cd path\to\HousePurchaseConciergeBot
```

### 2. 仮想環境を作成

プロジェクト専用の Python 環境（`.venv`）を作成します。

```powershell
python -m venv .venv
```

> 仮想環境とは、プロジェクトごとに独立した Python 実行環境のことです。
> グローバル環境を汚さず、プロジェクト間でライブラリのバージョン衝突を防げます。

### 3. 仮想環境をアクティベート

```powershell
.\.venv\Scripts\Activate.ps1
```

成功するとプロンプトの先頭に `(.venv)` が表示されます。

> **PowerShell で実行ポリシーエラーが出る場合**
>
> 以下のいずれかで対処してください。
>
> ```powershell
> # 一時的に許可（このセッションのみ）
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
>
> # ユーザー全体で許可（推奨・1回だけ実行すれば OK）
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

### 4. pip を最新化

```powershell
python -m pip install --upgrade pip
```

### 5. プロジェクトと依存ライブラリをインストール

開発用ツール（pytest, ruff, black など）も含めてインストールします。

```powershell
pip install -e ".[dev]"
```

- `-e` : editable モード。コードを編集すると即座に反映されます。
- `.` : カレントディレクトリ（このプロジェクト）をインストール。
- `[dev]` : `pyproject.toml` の `optional-dependencies` の `dev` グループも含める。

### 6. `.env` ファイルを作成

環境変数のテンプレート `.env.example` をコピーして、自分用の `.env` を作成します。

```powershell
Copy-Item .env.example .env
```

その後、`.env` を開いて各 API キーや設定値を入力してください。

> ⚠️ `.env` には秘密情報が入るため、絶対に Git にコミットしないでください。
> `.gitignore` で除外されています。

---

## 動作確認

セットアップが正常に完了したか、以下のコマンドで確認できます。

### インストール済みパッケージの確認

```powershell
pip list
```

`house-purchase-concierge-bot`, `pytest`, `ruff`, `black` などが表示されれば OK。

### 自作パッケージのインポート確認

```powershell
python -c "import app; print(app.__file__)"
```

このプロジェクトの `app\__init__.py` のパスが表示されれば、editable インストールが正しく機能しています。

### テストの実行

```powershell
pytest
```

### Lint チェック

```powershell
ruff check .
```

### コードフォーマットの確認

```powershell
# チェックのみ
black --check .

# 実際にフォーマット
black .
```

---

## 2 回目以降の開発開始手順

一度セットアップが終わっていれば、次回からは以下だけで開発を再開できます。

```powershell
cd path\to\HousePurchaseConciergeBot
.\.venv\Scripts\Activate.ps1
```

仮想環境から抜けるときは:

```powershell
deactivate
```

---

## プロジェクト構成

```
HousePurchaseConciergeBot/
├── app/                      # アプリケーション本体
│   ├── __init__.py
│   ├── config.py
│   ├── api/                  # API エンドポイント
│   ├── batch/                # バッチ処理
│   ├── domain/               # ドメインロジック
│   │   ├── models/
│   │   └── services/
│   ├── infra/                # 外部システム連携
│   │   ├── db/
│   │   ├── source_adapters/
│   │   ├── llm/
│   │   └── notifier/
│   └── schemas/              # データスキーマ
├── tests/                    # テストコード
├── docs/                     # ドキュメント
├── Tools/                    # 開発用ツール・スクリプト
├── .env.example              # 環境変数のテンプレート
├── .gitignore                # Git 管理外ファイルの設定
├── pyproject.toml            # プロジェクト設定・依存定義
└── README.md
```

---

## 開発時のよく使うコマンド一覧

| 用途                           | コマンド                          |
| ------------------------------ | --------------------------------- |
| 仮想環境に入る                 | `.\.venv\Scripts\Activate.ps1`    |
| 仮想環境から抜ける             | `deactivate`                      |
| 新しいライブラリを追加         | `pip install ライブラリ名`        |
| テスト実行                     | `pytest`                          |
| Lint チェック                  | `ruff check .`                    |
| Lint 自動修正                  | `ruff check . --fix`              |
| コードフォーマット             | `black .`                         |
| インストール済みパッケージ確認 | `pip list`                        |

---

## トラブルシューティング

### `.\.venv\Scripts\Activate.ps1` でエラーが出る

PowerShell の実行ポリシーが原因です。上記「3. 仮想環境をアクティベート」の補足を参照してください。

### `pip install -e ".[dev]"` で `[dev]` が認識されない

クォーテーション（`"`）で囲うのを忘れている可能性があります。PowerShell や bash では `[` がシェルに解釈されてしまうため、必ずクォートで囲ってください。

### `python -c "import app"` で `ModuleNotFoundError` が出る

仮想環境がアクティベートされていない、または `pip install -e ".[dev]"` が完了していない可能性があります。プロンプトの先頭に `(.venv)` が表示されているか確認してください。
