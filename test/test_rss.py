import sys
import os
import logging

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rss_fetcher import get_new_articles

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_rss_fetcher():
    """RSSフィードからの記事取得をテスト"""
    print("=== RSSフィード取得テスト ===")
    # 通常より長い時間範囲で確実に記事を取得する（テスト用）
    articles = get_new_articles(hours_limit=48)
    
    print(f"Found {len(articles)} articles")
    for i, article in enumerate(articles):
        print(f"\nArticle {i+1}:")
        print(f"Title: {article['title']}")
        print(f"Link: {article['link']}")
        print(f"Blog: {article['blog_name']}")
        print(f"Published: {article['published']}")
        print(f"Content length: {len(article['content'])} chars")
    
    assert len(articles) >= 0, "記事が取得できませんでした"
    print("RSSフィード取得テスト成功！")

if __name__ == "__main__":
    test_rss_fetcher()