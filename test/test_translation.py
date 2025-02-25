import sys
import os
import logging

# 親ディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.translator import TranslatorFactory
from src.rss_fetcher import get_new_articles

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def test_translation():
    """翻訳機能をテスト"""
    print("=== 翻訳機能テスト ===")
    
    # 1つの記事を取得（テスト用に時間範囲を広げる）
    articles = get_new_articles(hours_limit=48)
    
    if not articles:
        print("テスト用の記事がありません。RSSフィードの設定を確認してください。")
        return False
    
    # 最初の記事だけをテスト
    article = articles[0]
    print(f"\nTesting translation of article: {article['title']}")
    print(f"Content length: {len(article['content'])} chars")
    
    # 翻訳インスタンスを取得
    translator = TranslatorFactory.get_translator()
    
    # 翻訳を実行
    summary, translation = translator.translate_article(article)
    
    print("\n=== 翻訳結果 ===")
    print("\n【要約】")
    print(summary)
    print("\n【翻訳】")
    print(translation[:500] + "..." if len(translation) > 500 else translation)
    
    assert summary, "要約が生成されませんでした"
    assert translation, "翻訳が生成されませんでした"
    
    print("\n翻訳機能テスト成功！")
    return True

if __name__ == "__main__":
    test_translation()