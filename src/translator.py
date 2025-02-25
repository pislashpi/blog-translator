import logging
from typing import Dict, Any, Tuple
import config
from google import genai
#import openai
#from anthropic import Anthropic

logger = logging.getLogger(__name__)

class TranslatorFactory:
    @staticmethod
    def get_translator():
        """設定に基づいて適切な翻訳クラスのインスタンスを返す"""
        api = config.TRANSLATION_API
        
        if api == config.TranslationAPI.GEMINI:
            return GeminiTranslator()
        elif api == config.TranslationAPI.OPENAI:
            return OpenAITranslator()
        elif api == config.TranslationAPI.ANTHROPIC:
            return AnthropicTranslator()
        else:
            raise ValueError(f"Unsupported translation API: {api}")


class BaseTranslator:
    def translate_article(self, article: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        記事を翻訳し、要約と翻訳本文を返す
        
        Args:
            article: 翻訳する記事情報
            
        Returns:
            (翻訳タイトル, 要約, 翻訳本文)のタプル
        """
        raise NotImplementedError("Subclasses must implement translate_article")


class GeminiTranslator(BaseTranslator):
    def __init__(self):
        logger.info("Initializing Gemini translator")
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.GEMINI_MODEL
    
    def translate_article(self, article: Dict[str, Any]) -> Tuple[str, str, str]:
        prompt = f"""以下の英語記事を日本語に翻訳してください。記事タイトルの翻訳、2〜3行程度の要約、本文全体の翻訳が必要です。

タイトル: {article['title']}

元記事:
{article['content']}

出力形式:
【翻訳タイトル】
[ここに記事タイトルの日本語翻訳を書いてください]

【要約】
[ここに2〜3行の要約を日本語で書いてください]

【翻訳】
[ここに全文の翻訳を日本語で書いてください]
"""
        
        try:
            logger.info(f"Sending translation request to Gemini API for article: {article['title']}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            
            response_text = response.text
            
            # 翻訳タイトル、要約、翻訳部分を抽出
            parts = response_text.split("【翻訳タイトル】")
            if len(parts) > 1:
                parts = parts[1].split("【要約】")
                if len(parts) > 1:
                    translated_title = parts[0].strip()
                    parts = parts[1].split("【翻訳】")
                    if len(parts) > 1:
                        summary = parts[0].strip()
                        translation = parts[1].strip()
                        logger.info("Successfully translated with Gemini API")
                        return translated_title, summary, translation
            
            # 形式通りでない場合の処理
            logger.warning("Unexpected response format from Gemini API")
            return article['title'], "要約を取得できませんでした。", response_text
            
        except Exception as e:
            logger.error(f"Gemini API translation error: {e}")
            return article['title'], "翻訳エラーが発生しました。", f"翻訳エラー: {e}"


class OpenAITranslator(BaseTranslator):
    def __init__(self):
        logger.info("Initializing OpenAI translator")
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def translate_article(self, article: Dict[str, Any]) -> Tuple[str, str, str]:
        prompt = f"""以下の英語記事を日本語に翻訳してください。記事タイトルの翻訳、2〜3行程度の要約、本文全体の翻訳が必要です。

タイトル: {article['title']}

元記事:
{article['content']}

出力形式:
【翻訳タイトル】
[ここに記事タイトルの日本語翻訳を書いてください]

【要約】
[ここに2〜3行の要約を日本語で書いてください]

【翻訳】
[ここに全文の翻訳を日本語で書いてください]
"""
        
        try:
            logger.info(f"Sending translation request to OpenAI API for article: {article['title']}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは翻訳者です。英語の記事を日本語に翻訳し、タイトルの翻訳と要約も提供します。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            
            response_text = response.choices[0].message.content
            
            # 翻訳タイトル、要約、翻訳部分を抽出
            parts = response_text.split("【翻訳タイトル】")
            if len(parts) > 1:
                parts = parts[1].split("【要約】")
                if len(parts) > 1:
                    translated_title = parts[0].strip()
                    parts = parts[1].split("【翻訳】")
                    if len(parts) > 1:
                        summary = parts[0].strip()
                        translation = parts[1].strip()
                        logger.info("Successfully translated with OpenAI API")
                        return translated_title, summary, translation
            
            # 形式通りでない場合の処理
            logger.warning("Unexpected response format from OpenAI API")
            return article['title'], "要約を取得できませんでした。", response_text
            
        except Exception as e:
            logger.error(f"OpenAI API translation error: {e}")
            return article['title'], "翻訳エラーが発生しました。", f"翻訳エラー: {e}"


class AnthropicTranslator(BaseTranslator):
    def __init__(self):
        logger.info("Initializing Anthropic translator")
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.ANTHROPIC_MODEL
    
    def translate_article(self, article: Dict[str, Any]) -> Tuple[str, str, str]:
        prompt = f"""以下の英語記事を日本語に翻訳してください。記事タイトルの翻訳、2〜3行程度の要約、本文全体の翻訳が必要です。

タイトル: {article['title']}

元記事:
{article['content']}

出力形式:
【翻訳タイトル】
[ここに記事タイトルの日本語翻訳を書いてください]

【要約】
[ここに2〜3行の要約を日本語で書いてください]

【翻訳】
[ここに全文の翻訳を日本語で書いてください]
"""
        
        try:
            logger.info(f"Sending translation request to Anthropic API for article: {article['title']}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system="あなたは翻訳者です。英語の記事を日本語に翻訳し、タイトルの翻訳と要約も提供します。",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text
            
            # 翻訳タイトル、要約、翻訳部分を抽出
            parts = response_text.split("【翻訳タイトル】")
            if len(parts) > 1:
                parts = parts[1].split("【要約】")
                if len(parts) > 1:
                    translated_title = parts[0].strip()
                    parts = parts[1].split("【翻訳】")
                    if len(parts) > 1:
                        summary = parts[0].strip()
                        translation = parts[1].strip()
                        logger.info("Successfully translated with Anthropic API")
                        return translated_title, summary, translation
            
            # 形式通りでない場合の処理
            logger.warning("Unexpected response format from Anthropic API")
            return article['title'], "要約を取得できませんでした。", response_text
            
        except Exception as e:
            logger.error(f"Anthropic API translation error: {e}")
            return article['title'], "翻訳エラーが発生しました。", f"翻訳エラー: {e}"