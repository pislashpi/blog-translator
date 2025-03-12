import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

class ArticleDatabase:
    def __init__(self, db_path="processed_articles.db"):
        """
        処理済み記事を管理するデータベース
        
        Args:
            db_path: SQLiteデータベースファイルのパス
        """
        self.db_path = db_path
        self._initialize_db()
        logger.info(f"Initialized article database: {db_path}")
    
    def _initialize_db(self):
        """データベースとテーブルの初期化"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # processed_articlesテーブルを作成（存在しない場合）
        c.execute('''
        CREATE TABLE IF NOT EXISTS processed_articles (
            id INTEGER PRIMARY KEY,
            article_url TEXT UNIQUE,
            blog_name TEXT,
            processed_date TEXT,
            wp_post_id INTEGER
        )
        ''')
        
        # system_infoテーブルを作成（存在しない場合）
        c.execute('''
        CREATE TABLE IF NOT EXISTS system_info (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_article_processed(self, article_url: str) -> bool:
        """
        記事が処理済みかどうかをチェック
        
        Args:
            article_url: 記事のURL
            
        Returns:
            処理済みならTrue、そうでなければFalse
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT 1 FROM processed_articles WHERE article_url = ?", (article_url,))
        result = c.fetchone() is not None
        
        conn.close()
        return result
    
    def mark_article_processed(self, article_url: str, blog_name: str, wp_post_id: int) -> None:
        """
        記事を処理済みとしてマーク
        
        Args:
            article_url: 記事のURL
            blog_name: ブログ名
            wp_post_id: WordPress投稿ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        
        c.execute(
            "INSERT OR REPLACE INTO processed_articles (article_url, blog_name, processed_date, wp_post_id) VALUES (?, ?, ?, ?)",
            (article_url, blog_name, now, wp_post_id)
        )
        
        # 最終実行時刻を更新
        self.update_last_run_time()
        
        conn.commit()
        conn.close()
        logger.info(f"Marked article as processed: {article_url}, wp_post_id: {wp_post_id}")
    
    def get_processed_articles(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        処理済み記事のリストを取得
        
        Args:
            limit: 取得する記事数の上限（Noneの場合は全て）
            
        Returns:
            処理済み記事のリスト
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if limit:
            c.execute("SELECT * FROM processed_articles ORDER BY processed_date DESC LIMIT ?", (limit,))
        else:
            c.execute("SELECT * FROM processed_articles ORDER BY processed_date DESC")
        
        articles = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return articles
    
    def update_last_run_time(self, custom_time: str = None) -> None:
        """
        最終実行時刻を更新
        
        Args:
            custom_time: カスタム時刻（Noneの場合は現在時刻）
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = custom_time or datetime.now().isoformat()
        
        c.execute(
            "INSERT OR REPLACE INTO system_info (key, value) VALUES (?, ?)",
            ("last_run_time", now)
        )
        
        conn.commit()
        conn.close()
        logger.info(f"Updated last run time: {now}")
    
    def get_last_run_time(self) -> Optional[datetime]:
        """
        最終実行時刻を取得
        
        Returns:
            最終実行時刻（datetime）、存在しない場合はNone
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT value FROM system_info WHERE key = ?", ("last_run_time",))
        result = c.fetchone()
        
        conn.close()
        
        if result:
            try:
                return datetime.fromisoformat(result[0])
            except ValueError:
                logger.error(f"Invalid datetime format in database: {result[0]}")
                return None
        return None
    
    def get_last_processed_date(self) -> Optional[datetime]:
        """
        最後に処理した記事の日時を取得
        
        Returns:
            最終処理日時（datetime）、記事がない場合はNone
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT processed_date FROM processed_articles ORDER BY processed_date DESC LIMIT 1")
        result = c.fetchone()
        
        conn.close()
        
        if result:
            try:
                return datetime.fromisoformat(result[0])
            except ValueError:
                logger.error(f"Invalid datetime format in database: {result[0]}")
                return None
        return None