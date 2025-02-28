import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from src.config import Config

class NewsAnalyzer:
    def __init__(self):
        self.news_cache = {}
        self.sentiment_scores = {}
        
    def fetch_crypto_news(self, symbol: str) -> List[Dict]:
        """Fetch news related to cryptocurrency"""
        try:
            # Remove USDT from symbol for better news search
            search_term = symbol.replace('USDT', '')
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'cryptocurrency {search_term}',
                'apiKey': Config.NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                news_data = response.json()
                articles = news_data.get('articles', [])
                self.news_cache[symbol] = articles
                return articles
            else:
                logging.error(f"Failed to fetch news: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Error fetching news: {e}")
            return []
            
    def analyze_sentiment(self, articles: List[Dict]) -> float:
        """Simple sentiment analysis based on keywords"""
        try:
            positive_keywords = ['bullish', 'surge', 'gain', 'up', 'high', 'positive', 'growth']
            negative_keywords = ['bearish', 'drop', 'fall', 'down', 'low', 'negative', 'crash']
            
            total_score = 0
            for article in articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                content = f"{title} {description}"
                
                # Calculate sentiment score
                positive_count = sum(1 for word in positive_keywords if word in content)
                negative_count = sum(1 for word in negative_keywords if word in content)
                
                score = (positive_count - negative_count) / (positive_count + negative_count + 1)
                total_score += score
                
            return total_score / len(articles) if articles else 0
            
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return 0
            
    def get_market_sentiment(self, symbol: str) -> Dict:
        """Get overall market sentiment from news"""
        try:
            articles = self.fetch_crypto_news(symbol)
            sentiment_score = self.analyze_sentiment(articles)
            
            self.sentiment_scores[symbol] = sentiment_score
            
            return {
                'sentiment_score': sentiment_score,
                'sentiment': 'BULLISH' if sentiment_score > 0.2 else 'BEARISH' if sentiment_score < -0.2 else 'NEUTRAL',
                'confidence': abs(sentiment_score),
                'news_count': len(articles)
            }
            
        except Exception as e:
            logging.error(f"Error getting market sentiment: {e}")
            return {
                'sentiment_score': 0,
                'sentiment': 'NEUTRAL',
                'confidence': 0,
                'news_count': 0
            }
