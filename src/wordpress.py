import requests
from datetime import datetime
from typing import List, Dict, Any
import logging
import config
import webbrowser
import http.server
import socketserver
import urllib.parse
import threading
import time
import os

logger = logging.getLogger(__name__)

class OAuth2Handler(http.server.SimpleHTTPRequestHandler):
    """OAuth2リダイレクトを処理するハンドラ"""
    auth_code = None
    
    def do_GET(self):
        """GETリクエストを処理し、認証コードを取得"""
        query = urllib.parse.urlparse(self.path).query
        query_components = urllib.parse.parse_qs(query)
        
        if 'code' in query_components:
            OAuth2Handler.auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_text = '<html><body><h1>認証成功!</h1><p>このウィンドウは閉じて構いません。</p></body></html>'
            self.wfile.write(response_text.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_text = '<html><body><h1>認証エラー</h1><p>認証コードを取得できませんでした。</p></body></html>'
            self.wfile.write(error_text.encode('utf-8'))
    
    def log_message(self, format, *args):
        """ログ出力を抑制"""
        return


class WordPressPoster:
    def __init__(self):
        self.client_id = config.WP_CLIENT_ID
        self.client_secret = config.WP_CLIENT_SECRET
        self.redirect_uri = config.WP_REDIRECT_URI
        self.site_url = config.WP_SITE_URL
        self.api_base_url = "https://public-api.wordpress.com/wp/v2/sites"
        self.auth_url = "https://public-api.wordpress.com/oauth2/authorize"
        self.token_url = "https://public-api.wordpress.com/oauth2/token"
        
        # 保存されたトークンを読み込むか、新規取得
        self.access_token = self._load_access_token() or self._get_new_access_token()
        
        logger.info(f"Initialized WordPress poster with site URL: {self.site_url}")
    
    def _load_access_token(self):
        """保存されたアクセストークンを読み込む"""
        token_file = "wp_access_token.txt"
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                return f.read().strip()
        return None
    
    def _save_access_token(self, token):
        """アクセストークンを保存"""
        with open("wp_access_token.txt", "w") as f:
            f.write(token)
    
    def _get_auth_code(self):
        """ブラウザを開いてOAuth2認証コードを取得"""
        # 認証URLを構築
        auth_params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "global"  # postsからglobalに変更
        }
        
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(auth_params)}"
        
        # ローカルサーバーを起動して認証コードを待機
        server = socketserver.TCPServer(("localhost", 8000), OAuth2Handler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # ブラウザで認証URLを開く
        print(f"ブラウザが開き、WordPress.comでの認証が求められます。")
        webbrowser.open(auth_url)
        
        # 認証コードを待機
        timeout = 300  # 5分
        start_time = time.time()
        while OAuth2Handler.auth_code is None:
            if time.time() - start_time > timeout:
                server.shutdown()
                raise TimeoutError("認証タイムアウト：コードが取得できませんでした。")
            time.sleep(1)
        
        auth_code = OAuth2Handler.auth_code
        server.shutdown()
        
        return auth_code
    
    def _get_new_access_token(self):
        """OAuth2フローでアクセストークンを取得"""
        try:
            # 認証コードを取得
            auth_code = self._get_auth_code()
            
            # アクセストークンを取得
            token_params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(self.token_url, data=token_params)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise ValueError("アクセストークンを取得できませんでした。")
            
            # トークンを保存
            self._save_access_token(access_token)
            
            return access_token
            
        except Exception as e:
            logger.error(f"OAuth2認証エラー: {e}")
            raise
    
    def post_article(self, title: str, content: str, status: str = 'publish') -> Dict[str, Any]:
        """
        WordPress.comに記事を投稿
        
        Args:
            title: 記事のタイトル
            content: 記事の内容（Markdown）
            status: 公開ステータス（'publish', 'draft', 'private', etc.）
            
        Returns:
            APIレスポンス（辞書形式）
        """
        endpoint = f"{self.api_base_url}/{self.site_url}/posts"
        
        # API v2はJSONフォーマットを使用
        data = {
            'title': title,
            'content': content,
            'status': status,
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"Posting article to WordPress: {title}")
        response = requests.post(endpoint, json=data, headers=headers)
        
        try:
            response.raise_for_status()
            logger.info(f"Successfully posted article: {title}, ID: {response.json().get('id')}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error posting to WordPress: {e}")
            logger.error(f"Response: {response.text}")
            
            # トークンが無効な場合は再取得を試みる
            if response.status_code == 401:
                logger.info("Access token might be expired, trying to get a new one...")
                self.access_token = self._get_new_access_token()
                return self.post_article(title, content, status)
            
            raise
    
    def post_translated_article(self, article: Dict[str, Any], translated_title: str, summary: str, translation: str) -> Dict[str, Any]:
        """
        翻訳記事をWordPressに投稿
        
        Args:
            article: 元記事の情報
            translated_title: 翻訳したタイトル
            summary: 翻訳した要約
            translation: 翻訳した本文
            
        Returns:
            投稿したWordPress記事の情報（辞書形式）
        """
        # タイトルを作成：「翻訳後のタイトル + 翻訳前のブログの名前」
        title = f"{translated_title} ({article['blog_name']})"
        
        # 改行をHTMLの段落に変換
        translation_html = ""
        for paragraph in translation.split('\n\n'):
            if paragraph.strip():
                # 段落内の改行を<br>に変換
                paragraph = paragraph.replace('\n', '<br />')
                translation_html += f"<!-- wp:paragraph -->\n<p>{paragraph}</p>\n<!-- /wp:paragraph -->\n\n"
        
        # 本文を構築 (Gutenbergブロックフォーマット)
        content = f"""<!-- wp:paragraph -->
<p><strong>元記事:</strong> <a href="{article['link']}">{article['link']}</a></p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>要約</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{summary.replace('\n', '<br />')}</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>翻訳</h2>
<!-- /wp:heading -->

{translation_html}
"""
        
        return self.post_article(title, content)
    
    def post_summary_article(self, translated_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        翻訳した記事のまとめ記事を投稿
        
        Args:
            translated_articles: 翻訳済み記事のリスト。各記事には以下のキーが必要:
                - wp_id: WordPress記事ID
                - title: 記事タイトル
                - summary: 要約文
                
        Returns:
            投稿したWordPress記事の情報（辞書形式）
        """
        today = datetime.now().strftime("%Y年%m月%d日")
        title = f"{today}の記事"
        
        content = """<!-- wp:heading -->
<h2>本日翻訳した記事</h2>
<!-- /wp:heading -->

"""
        
        for article in translated_articles:
            content += f"""<!-- wp:heading {"level":3} -->
<h3><a href="/?p={article['wp_id']}">{article['title']}</a></h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{article['summary']}</p>
<!-- /wp:paragraph -->

"""
        
        return self.post_article(title, content)