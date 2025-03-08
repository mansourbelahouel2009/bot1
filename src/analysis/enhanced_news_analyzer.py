
import logging
import requests
import re
import nltk
from textblob import TextBlob
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# تغيير استيراد النموذج من مطلق إلى نسبي
from ..config import Config
from ..database.models import DatabaseManager

class EnhancedNewsAnalyzer:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.news_cache = {}
        self.sentiment_scores = {}
        self.supported_languages = ['en', 'ar', 'zh', 'es', 'fr']  # اللغات المدعومة
        
        # تحميل الموارد اللازمة لمعالجة اللغة الطبيعية
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            logging.error(f"Error downloading NLTK resources: {e}")

    def fetch_crypto_news(self, symbol: str, languages: List[str] = ['en']) -> List[Dict]:
        """جلب الأخبار المتعلقة بالعملة المشفرة بلغات متعددة"""
        try:
            all_articles = []
            search_term = symbol.replace('USDT', '')
            
            for lang in languages:
                if lang not in self.supported_languages:
                    continue
                    
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'q': f'cryptocurrency {search_term}',
                    'apiKey': Config.NEWS_API_KEY,
                    'language': lang,
                    'sortBy': 'publishedAt',
                    'pageSize': 10,
                    'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    articles = news_data.get('articles', [])
                    
                    # معالجة كل مقال
                    for article in articles:
                        processed_article = self._process_article(article, lang)
                        if processed_article:
                            all_articles.append(processed_article)
                            
                else:
                    logging.error(f"Failed to fetch news for language {lang}: {response.status_code}")
            
            # حفظ في قاعدة البيانات
            if all_articles:
                self.db_manager.save_news_analysis(symbol, {
                    'articles': all_articles,
                    'timestamp': datetime.now()
                })
            
            return all_articles
            
        except Exception as e:
            logging.error(f"Error fetching news: {e}")
            return []

    def _process_article(self, article: Dict, language: str) -> Optional[Dict]:
        """معالجة المقال وتنظيفه"""
        try:
            # استخراج النص
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # تنظيف النص
            title = self._clean_text(title)
            description = self._clean_text(description)
            content = self._clean_text(content)
            
            # تقسيم النص الطويل
            if content and len(content) > 520:
                content = self._split_long_text(content)
            
            # تحليل المشاعر
            sentiment = self._analyze_text_sentiment(f"{title} {description} {content}", language)
            
            return {
                'title': title,
                'description': description,
                'content': content,
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', ''),
                'language': language,
                'sentiment': sentiment
            }
            
        except Exception as e:
            logging.error(f"Error processing article: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """تنظيف النص من الرموز غير المرغوب فيها"""
        if not text:
            return ""
            
        # حذف الروابط
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # استبدال الرموز التعبيرية بوصفها
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # حذف الأرقام والرموز الخاصة مع الحفاظ على النص
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', ' ', text)
        
        # تنظيف المسافات المتعددة
        text = ' '.join(text.split())
        
        return text

    def _split_long_text(self, text: str) -> str:
        """تقسيم النص الطويل إلى جمل"""
        try:
            sentences = nltk.sent_tokenize(text)
            total_length = 0
            selected_sentences = []
            
            for sentence in sentences:
                if total_length + len(sentence) <= 520:
                    selected_sentences.append(sentence)
                    total_length += len(sentence)
                else:
                    break
            
            return ' '.join(selected_sentences)
            
        except Exception as e:
            logging.error(f"Error splitting text: {e}")
            return text[:520] if len(text) > 520 else text

    def _analyze_text_sentiment(self, text: str, language: str) -> Dict:
        """تحليل مشاعر النص"""
        try:
            blob = TextBlob(text)
            
            # تحليل المشاعر
            sentiment_polarity = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity
            
            # تصنيف المشاعر
            if sentiment_polarity > 0.3:
                sentiment = 'BULLISH'
            elif sentiment_polarity < -0.3:
                sentiment = 'BEARISH'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'sentiment': sentiment,
                'polarity': sentiment_polarity,
                'subjectivity': sentiment_subjectivity,
                'confidence': abs(sentiment_polarity)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'polarity': 0,
                'subjectivity': 0,
                'confidence': 0
            }

    def get_market_sentiment(self, symbol: str, languages: List[str] = ['en']) -> Dict:
        """الحصول على تحليل شامل لمشاعر السوق"""
        try:
            articles = self.fetch_crypto_news(symbol, languages)
            if not articles:
                return self._get_default_sentiment()
            
            total_polarity = 0
            total_confidence = 0
            sentiment_distribution = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
            
            for article in articles:
                sentiment_data = article.get('sentiment', {})
                sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
                polarity = sentiment_data.get('polarity', 0)
                confidence = sentiment_data.get('confidence', 0)
                
                total_polarity += polarity
                total_confidence += confidence
                sentiment_distribution[sentiment] += 1
            
            num_articles = len(articles)
            avg_polarity = total_polarity / num_articles if num_articles > 0 else 0
            avg_confidence = total_confidence / num_articles if num_articles > 0 else 0
            
            # تحديد المشاعر الإجمالية
            if avg_polarity > 0.3:
                overall_sentiment = 'BULLISH'
            elif avg_polarity < -0.3:
                overall_sentiment = 'BEARISH'
            else:
                overall_sentiment = 'NEUTRAL'
            
            sentiment_analysis = {
                'sentiment': overall_sentiment,
                'confidence': avg_confidence,
                'polarity': avg_polarity,
                'distribution': sentiment_distribution,
                'news_count': num_articles,
                'languages_analyzed': languages
            }
            
            # حفظ التحليل في قاعدة البيانات
            self.db_manager.save_news_analysis(symbol, sentiment_analysis)
            
            return sentiment_analysis
            
        except Exception as e:
            logging.error(f"Error getting market sentiment: {e}")
            return self._get_default_sentiment()

    def _get_default_sentiment(self) -> Dict:
        """إرجاع تحليل مشاعر افتراضي"""
        return {
            'sentiment': 'NEUTRAL',
            'confidence': 0,
            'polarity': 0,
            'distribution': {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0},
            'news_count': 0,
            'languages_analyzed': []
        }
