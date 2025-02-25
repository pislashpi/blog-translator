import os
from dotenv import load_dotenv
from enum import Enum

# .envファイルから環境変数を読み込む
load_dotenv()

class TranslationAPI(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

# 使用する翻訳API
TRANSLATION_API = TranslationAPI(os.getenv("TRANSLATION_API", "gemini"))

# 翻訳元言語と翻訳先言語
SOURCE_LANGUAGE = "en"
TARGET_LANGUAGE = "ja"

# RSSフィードのURL（複数）
RSS_FEEDS = [
    {"name": "Psypost", "url": os.getenv("RSS_FEED_A")},
    {"name": "Neuroscience News", "url": os.getenv("RSS_FEED_B")},
    {"name": "ブログC", "url": os.getenv("RSS_FEED_C")},
    # 必要に応じて追加
]

# 記事取得の制限時間（現在時刻からX時間前）
HOURS_LIMIT = 24

# WordPress.com OAuth2設定
WP_SITE_URL = os.getenv("WP_SITE_URL")  # サイトURL（例：your-site.wordpress.com）または数値ID
WP_CLIENT_ID = os.getenv("WP_CLIENT_ID")
WP_CLIENT_SECRET = os.getenv("WP_CLIENT_SECRET")
WP_REDIRECT_URI = os.getenv("WP_REDIRECT_URI", "http://localhost:8000/")

# API鍵
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 翻訳APIのモデル設定
GEMINI_MODEL = "gemini-2.0-flash-lite-preview-02-05"
OPENAI_MODEL = "gpt-4o" 
ANTHROPIC_MODEL = "claude-3-sonnet-20240229"