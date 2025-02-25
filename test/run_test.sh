#!/bin/bash
# テストを順番に実行するスクリプト

echo "===== ブログ翻訳システム テスト ====="
echo ""

# 1. RSSフィードからの記事取得テスト
echo "1. RSSフィードからの記事取得テスト"
python tests/test_rss.py
if [ $? -ne 0 ]; then
    echo "RSSテストに失敗しました。次のテストに進みません。"
    exit 1
fi

echo ""
echo "次のテストを実行しますか？ (y/n)"
read answer
if [ "$answer" != "y" ]; then
    echo "テストを中止します。"
    exit 0
fi

# 2. 翻訳機能のテスト
echo ""
echo "2. 翻訳機能のテスト"
python tests/test_translation.py
if [ $? -ne 0 ]; then
    echo "翻訳テストに失敗しました。次のテストに進みません。"
    exit 1
fi

echo ""
echo "次のテストを実行しますか？ (y/n)"
read answer
if [ "$answer" != "y" ]; then
    echo "テストを中止します。"
    exit 0
fi

# 3. WordPress投稿テスト
echo ""
echo "3. WordPress投稿テスト"
python tests/test_wordpress.py
if [ $? -ne 0 ]; then
    echo "WordPress投稿テストに失敗しました。"
    exit 1
fi

echo ""
echo "すべてのテストが完了しました！"
echo "本番環境で実行するには: python src/main.py"