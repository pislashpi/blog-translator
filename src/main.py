import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
import os

    # 自作モジュールのインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rss_fetcher import get_new_articles
from src.translator import TranslatorFactory
from src.wordpress import WordPressPoster
from src.db import ArticleDatabase
from src.article_scraper import ArticleScraper
import config

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("blog_translator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("blog_translator")

def main():
    logger.info("Blog translation process started")
    
    # 処理済み記事のデータベースを初期化
    db = ArticleDatabase()
    
    # RSSフィードから新しい記事を取得
    logger.info(f"Fetching new articles from the last {config.HOURS_LIMIT} hours")
    new_articles = get_new_articles(hours_limit=config.HOURS_LIMIT)
    logger.info(f"Found {len(new_articles)} new articles")
    
    if not new_articles:
        logger.info("No new articles found, exiting")
        return
    
    # スクレイパーの初期化
    scraper = ArticleScraper()
    
    # 翻訳インスタンスを取得
    translator = TranslatorFactory.get_translator()
    
    # WordPressポスターを初期化
    wp_poster = WordPressPoster()
    
    # 各記事を処理
    translated_articles = []
    
    for article in new_articles:
        article_url = article["link"]
        
        # 既に処理済みの記事はスキップ
        if db.is_article_processed(article_url):
            logger.info(f"Article already processed: {article_url}")
            continue
        
        logger.info(f"Processing article: {article['title']} from {article['blog_name']}")
        
        try:
            # RSSの内容が不十分な場合、記事の全文を取得
            logger.info("Checking if article content is sufficient...")
            if len(article['content']) < 500:  # 内容が少ない場合
                logger.info(f"Article content is too short ({len(article['content'])} chars). Fetching full content...")
                article = scraper.get_full_content(article)
            
            # 記事を翻訳
            logger.info("Translating article...")
            translated_title, summary, translation = translator.translate_article(article)
            
            # WordPressに投稿
            logger.info("Posting translated article to WordPress...")
            wp_response = wp_poster.post_translated_article(article, translated_title, summary, translation)
            
            # 処理済みとしてマーク
            wp_post_id = wp_response.get("id", 0)
            db.mark_article_processed(article_url, article["blog_name"], wp_post_id)
            
            # まとめ記事用に保存
            translated_articles.append({
                "wp_id": wp_post_id,
                "title": f"{article['title']} ({article['blog_name']})",
                "summary": summary
            })
            
            logger.info(f"Article successfully translated and posted: ID={wp_post_id}")
            
        except Exception as e:
            logger.error(f"Error processing article {article_url}: {e}")
    
    # 翻訳した記事がある場合、まとめ記事を投稿
    if translated_articles:
        logger.info(f"Posting summary article with {len(translated_articles)} articles...")
        try:
            wp_poster.post_summary_article(translated_articles)
            logger.info("Summary article posted successfully")
        except Exception as e:
            logger.error(f"Error posting summary article: {e}")
    else:
        logger.info("No new articles were translated, skipping summary article")
    
    logger.info("Blog translation process completed")

if __name__ == "__main__":
    main()