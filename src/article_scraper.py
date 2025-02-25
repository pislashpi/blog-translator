import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ArticleScraper:
    def __init__(self, headers=None):
        """
        記事スクレイピング用のクラス
        
        Args:
            headers: リクエストヘッダー（任意）
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    
    def get_full_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        記事URLから本文を取得し、article辞書を更新
        
        Args:
            article: 記事情報を含む辞書（'link'キーが必要）
            
        Returns:
            更新された記事情報
        """
        url = article['link']
        
        # 既に十分な内容がある場合はスキップ
        if len(article.get('content', '')) > 1000:
            logger.info(f"記事は既に十分な内容があります: {url}")
            return article
        
        try:
            logger.info(f"記事の全文を取得中: {url}")
            
            # URLのドメインからサイトタイプを判定
            domain = urlparse(url).netloc
            
            # 記事を取得
            full_content = self._scrape_article(url, domain)
            
            if full_content:
                # 取得した本文で更新
                article['content'] = full_content
                logger.info(f"記事の全文取得に成功: {url} ({len(full_content)} 文字)")
            else:
                logger.warning(f"記事の本文を抽出できませんでした: {url}")
            
            return article
            
        except Exception as e:
            logger.error(f"記事の取得中にエラー: {url} - {e}")
            return article
    
    def _scrape_article(self, url: str, domain: str) -> Optional[str]:
        """
        URLから記事本文をスクレイピング
        
        Args:
            url: 記事のURL
            domain: URLのドメイン
            
        Returns:
            記事の本文テキスト、取得できない場合はNone
        """
        # サイトに負荷をかけないよう少し待機
        time.sleep(2)
        
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # サイトタイプに応じた本文抽出ロジック
        content = None
        
        # Medium系のブログ
        if 'medium.com' in domain:
            article_tags = soup.select('article')
            if article_tags:
                # セクション内のテキストを抽出
                paragraphs = article_tags[0].select('p')
                content = '\n\n'.join([p.get_text() for p in paragraphs])
        
        # WordPress系のブログ
        elif any(wp_term in domain for wp_term in ['wordpress', 'wp.com']):
            content_div = soup.select('.entry-content, .post-content, .content, article')
            if content_div:
                paragraphs = content_div[0].select('p')
                content = '\n\n'.join([p.get_text() for p in paragraphs])
        
        # 一般的な記事ページの検出方法
        if not content:
            # 一般的な記事コンテナの検出
            article_containers = soup.select('article, .article, .post, .entry, .content, [itemprop="articleBody"]')
            if article_containers:
                paragraphs = article_containers[0].select('p')
                content = '\n\n'.join([p.get_text() for p in paragraphs])
            
            # 一般的な方法でも取得できない場合、ページ内のすべての段落を取得
            if not content:
                # ヘッダーとフッターを避ける
                main_content = soup.select('main, #main, .main, #content, .content')
                target = main_content[0] if main_content else soup
                
                # すべての段落を取得
                paragraphs = target.select('p')
                if paragraphs:
                    content = '\n\n'.join([p.get_text() for p in paragraphs])
        
        return content