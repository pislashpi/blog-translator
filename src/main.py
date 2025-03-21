import sys
import logging
from datetime import datetime, timedelta
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
    
    # 前回の実行時刻を取得
    last_run_time = db.get_last_run_time()
    
    if last_run_time:
        logger.info(f"Last execution time: {last_run_time.isoformat()}")
        # 前回の実行時刻から現在までの記事を取得
        new_articles = get_new_articles(since_date=last_run_time)
    else:
        # 初回実行または情報がない場合はデフォルトの時間範囲で実行
        logger.info(f"No previous execution records. Using default time limit: {config.HOURS_LIMIT} hours")
        new_articles = get_new_articles(hours_limit=config.HOURS_LIMIT)
        # 初回実行時は最終実行時刻を記録
        db.update_last_run_time()
    
    logger.info(f"Found {len(new_articles)} new articles")
    
    if not new_articles:
        logger.info("No new articles found, exiting")
        return
    
    # 記事を古い順に並び替え（投稿日時の昇順）
    new_articles.sort(key=lambda x: x['published'])
    logger.info("Articles sorted by publication date (oldest first)")
    
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
                "title": f"{translated_title} ({article['blog_name']})",
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
    
    # 最終実行時刻を更新
    db.update_last_run_time()
    logger.info("Blog translation process completed")

if __name__ == "__main__":
    main()