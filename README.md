# ブログ翻訳・自動投稿システム

このプロジェクトは、複数の英語ブログから記事を自動的に取得し、日本語に翻訳して WordPress.com ブログに投稿するシステムです。

## 機能

- 複数の英語ブログのRSSフィードから記事を取得
- RSSで本文が不十分な場合は元記事をスクレイピングして全文取得
- 前日から追加された記事を翻訳（英語→日本語）
  - タイトルの翻訳
  - 記事の要約（2〜3行）
  - 本文の翻訳
- 翻訳した記事をWordPress.comブログに投稿
- 翻訳した記事のまとめ記事も作成して投稿
- 複数の翻訳APIに対応（Gemini, OpenAI, Anthropic）
- 自然な段落・改行を保持した読みやすいレイアウト

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
   - WordPress.comのOAuth2認証情報

### WordPress.com APIの設定

1. [WordPress.com Developer Portal](https://developer.wordpress.com/apps/)で新しいアプリケーションを登録
2. 以下の情報を取得し、`.env`ファイルに設定
   - クライアントID
   - クライアントシークレット
3. リダイレクトURLに `http://localhost:8000/` を設定

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
   ※ 初回実行時はブラウザでWordPress.comの認証が求められます

### テストの一括実行

```
chmod +x run_tests.sh
./run_tests.sh
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
- WordPress.comのOAuth2認証設定

## ファイル構成

- `src/main.py` - メインスクリプト
- `src/rss_fetcher.py` - RSSフィードから記事を取得
- `src/article_scraper.py` - 記事本文のスクレイピング
- `src/translator.py` - 翻訳APIのラッパー
- `src/wordpress.py` - WordPressへの投稿（OAuth2認証）
- `src/db.py` - 処理済み記事の管理
- `tests/` - テストスクリプト
- `config.py` - 設定ファイル
- `.env` - 環境変数（API鍵など）

## 出力形式

### 個別記事の形式

- タイトル：「翻訳済みのタイトル (元ブログ名)」
- 本文：
  - 元記事へのリンク
  - 2〜3行の日本語要約
  - 記事の翻訳（段落と改行を保持）

### まとめ記事の形式

- タイトル：「YYYY年M月D日の記事」
- 本文：
  - 翻訳した記事へのリンク付きタイトル
  - 各記事の要約

## 注意事項

- 初回実行時には過去24時間以内の記事のみを対象とします
