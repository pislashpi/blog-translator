import sys
import os
import logging

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wordpress import WordPressPoster

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_wordpress_connection():
    """WordPressへの接続テスト（OAuth2認証）"""
    print("=== WordPress接続テスト（OAuth2認証） ===")
    print("注意: ブラウザウィンドウが開き、WordPress.comの認証ページが表示されます。")
    print("指示に従って認証を完了してください。")
    
    try:
        # WordPressPosterのインスタンス化で認証フローが実行される
        wp = WordPressPoster()
        
        # テスト投稿（ドラフトとして保存）
        title = "テスト投稿 - OAuth2テスト"
        content = """<!-- wp:paragraph -->
<p>これはテスト投稿です。このコンテンツはOAuth2認証を使用して投稿されました。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li>テスト項目1</li>
<li>テスト項目2</li>
<li>テスト項目3</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p><a href="https://example.com">リンクテスト</a></p>
<!-- /wp:paragraph -->
"""
        
        response = wp.post_article(title, content, status="draft")
        print(f"Post created: ID={response.get('id')}, URL={response.get('link')}")
        assert response.get('id'), "投稿IDが取得できませんでした"
        print("WordPress接続テスト成功！")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_wordpress_connection()