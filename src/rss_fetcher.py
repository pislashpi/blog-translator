import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import config

logger = logging.getLogger(__name__)

def get_new_articles(hours_limit: int = config.HOURS_LIMIT) -> List[Dict[str, Any]]:
    """
    RSSフィードから指定時間以内に投稿された新しい記事を取得する

    Args:
        hours_limit: 何時間前までの記事を取得するか

    Returns:
        新しい記事のリスト。各記事は辞書形式で、以下のキーを含む:
        - title: 記事のタイトル
        - link: 記事のURL
        - published: 投稿日時
        - content: 記事の内容
        - blog_name: ブログ名
    """
    time_limit = datetime.now() - timedelta(hours=hours_limit)
    new_articles = []

    for feed_info in config.RSS_FEEDS:
        feed_url = feed_info["url"]
        blog_name = feed_info["name"]

        if not feed_url:
            logger.warning(f"Feed URL for {blog_name} is not set. Skipping.")
            continue

        try:
            logger.info(f"Fetching RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # 投稿日時を解析
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    # 日付が取得できない場合は現在時刻とする（テスト用）
                    logger.warning(f"No date found for entry: {entry.title}. Using current time.")
                    pub_date = datetime.now()

                # 指定時間以内の記事のみ処理
                if pub_date >= time_limit:
                    # 記事の内容を取得
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    else:
                        content = ""

                    new_articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": pub_date,
                        "content": content,
                        "blog_name": blog_name
                    })
                    logger.info(f"Found new article: {entry.title} from {blog_name}")

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")

    logger.info(f"Total new articles found: {len(new_articles)}")
    return new_articles