# ブログ翻訳・自動投稿システム

このプロジェクトは、複数の英語ブログから記事を自動的に取得し、日本語に翻訳して WordPress.com ブログに投稿するシステムです。

## 機能

- 複数の英語ブログのRSSフィードから記事を取得
- 前日から追加された記事を翻訳（英語→日本語）
- 翻訳した記事をWordPress.comブログに投稿
- 翻訳した記事のまとめ記事も作成して投稿
- 複数の翻訳APIに対応（Gemini, OpenAI, Anthropic）

## セットアップ

### 必要条件

- Python 3.9以上
- [Rye](https://rye-up.com/)（Pythonパッケージマネージャー）

### インストール手順

1. リポジトリをクローン
   ```
   git clone https://github.com/yourusername/blog-translator.git
   cd blog-translator
   ```

2. Ryeでプロジェクトをセットアップ
   ```
   rye sync
   ```

3. `.env.example`を`.env`にコピーして必要な情報を入力
   ```
   cp .env.example .env
   ```

4. `.env`ファイルを編集して以下の情報を設定
   - 翻訳APIのキー（Gemini, OpenAI, Anthropic）
   - RSSフィードのURL
   - WordPress.comの認証情報

## 使用方法

### テスト実行

1. RSSフィードからの記事取得テスト
   ```
   python tests/test_rss.py
   ```

2. 翻訳機能のテスト
   ```
   python tests/test_translation.py
   ```

3. WordPress投稿テスト
   ```
   python tests/test_wordpress.py
   ```

### 本番実行

```
python src/main.py
```

### 定期実行の設定（cron）

毎朝8時に実行するためのcrontab設定例：

```
0 8 * * * cd /path/to/blog-translator && /path/to/python src/main.py >> /path/to/cron.log 2>&1
```

## 設定

設定は`config.py`ファイルで管理され、環境変数から読み込まれます。以下の設定が可能です：

- 使用する翻訳API（Gemini, OpenAI, Anthropic）
- 翻訳元・翻訳先の言語
- RSSフィードのURL
- 記事取得の時間範囲
- WordPress.comの設定

## ファイル構成

- `src/main.py` - メインスクリプト
- `src/rss_fetcher.py` - RSSフィードから記事を取得
- `src/translator.py` - 翻訳APIのラッパー
- `src/wordpress.py` - WordPressへの投稿
- `src/db.py` - 処理済み記事の管理
- `tests/` - テストスクリプト
- `config.py` - 設定ファイル
- `.env` - 環境変数（API鍵など）

## ライセンス

MIT