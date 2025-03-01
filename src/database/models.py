from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
import logging
import os

class DatabaseManager:
    def __init__(self):
        try:
            # Using environment variable for MongoDB connection
            mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
            self.client = MongoClient(mongo_url)
            self.db = self.client['crypto_trading']

            # إنشاء Collections
            self.market_data = self.db['market_data']
            self.technical_analysis = self.db['technical_analysis']
            self.news_analysis = self.db['news_analysis']
            self.trades = self.db['trades']

            # إنشاء Indexes
            self.market_data.create_index([("symbol", 1), ("timestamp", -1)])
            self.news_analysis.create_index([("symbol", 1), ("timestamp", -1)])
            self.technical_analysis.create_index([("symbol", 1), ("timestamp", -1)])

            logging.info("تم الاتصال بقاعدة البيانات MongoDB بنجاح")
        except Exception as e:
            logging.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            # Initialize empty collections for testing
            self._initialize_test_collections()

    def _initialize_test_collections(self):
        """Initialize empty collections for testing when MongoDB is not available"""
        self.market_data = []
        self.technical_analysis = []
        self.news_analysis = []
        self.trades = []
        logging.info("تم تهيئة مجموعات البيانات للاختبار")

    def save_market_data(self, symbol: str, data: Dict) -> None:
        """حفظ بيانات السوق"""
        try:
            if isinstance(self.market_data, list):
                self.market_data.append({**data, 'symbol': symbol, 'timestamp': datetime.now()})
            else:
                data['symbol'] = symbol
                data['timestamp'] = datetime.now()
                self.market_data.insert_one(data)
        except Exception as e:
            logging.error(f"خطأ في حفظ بيانات السوق: {e}")

    def save_technical_analysis(self, symbol: str, analysis: Dict) -> None:
        """حفظ نتائج التحليل الفني"""
        try:
            if isinstance(self.technical_analysis, list):
                self.technical_analysis.append({**analysis, 'symbol': symbol, 'timestamp': datetime.now()})
            else:
                analysis['symbol'] = symbol
                analysis['timestamp'] = datetime.now()
                self.technical_analysis.insert_one(analysis)
        except Exception as e:
            logging.error(f"خطأ في حفظ التحليل الفني: {e}")

    def save_news_analysis(self, symbol: str, news_data: Dict) -> None:
        """حفظ تحليل الأخبار"""
        try:
            if isinstance(self.news_analysis, list):
                self.news_analysis.append({**news_data, 'symbol': symbol, 'timestamp': datetime.now()})
            else:
                news_data['symbol'] = symbol
                news_data['timestamp'] = datetime.now()
                self.news_analysis.insert_one(news_data)
        except Exception as e:
            logging.error(f"خطأ في حفظ تحليل الأخبار: {e}")

    def save_trade(self, trade_data: Dict) -> None:
        """حفظ معلومات التداول"""
        try:
            if isinstance(self.trades, list):
                self.trades.append({**trade_data, 'timestamp': datetime.now()})
            else:
                trade_data['timestamp'] = datetime.now()
                self.trades.insert_one(trade_data)
        except Exception as e:
            logging.error(f"خطأ في حفظ معلومات التداول: {e}")

    def get_recent_market_data(self, symbol: str, limit: int = 100) -> List[Dict]:
        """استرجاع أحدث بيانات السوق"""
        try:
            if isinstance(self.market_data, list):
                return sorted([item for item in self.market_data if item.get('symbol') == symbol], key=lambda x: x['timestamp'], reverse=True)[:limit]
            return list(self.market_data.find(
                {'symbol': symbol},
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logging.error(f"خطأ في استرجاع بيانات السوق: {e}")
            return []

    def get_latest_technical_analysis(self, symbol: str) -> Optional[Dict]:
        """استرجاع آخر تحليل فني"""
        try:
            if isinstance(self.technical_analysis, list):
                return next((item for item in self.technical_analysis if item.get('symbol') == symbol), None)
            return self.technical_analysis.find_one(
                {'symbol': symbol},
                {'_id': 0},
                sort=[('timestamp', -1)]
            )
        except Exception as e:
            logging.error(f"خطأ في استرجاع التحليل الفني: {e}")
            return None

    def get_recent_news_analysis(self, symbol: str, limit: int = 10) -> List[Dict]:
        """استرجاع أحدث تحليلات الأخبار"""
        try:
            if isinstance(self.news_analysis, list):
                return sorted([item for item in self.news_analysis if item.get('symbol') == symbol], key=lambda x: x['timestamp'], reverse=True)[:limit]

            return list(self.news_analysis.find(
                {'symbol': symbol},
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logging.error(f"خطأ في استرجاع تحليلات الأخبار: {e}")
            return []

    def get_trades_report(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """استرجاع تقرير التداولات"""
        try:
            if isinstance(self.trades, list):
                return sorted([item for item in self.trades if start_date <= item.get('timestamp') <= end_date], key=lambda x: x['timestamp'], reverse=True)
            return list(self.trades.find(
                {
                    'timestamp': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                },
                {'_id': 0}
            ).sort('timestamp', -1))
        except Exception as e:
            logging.error(f"خطأ في استرجاع تقرير التداولات: {e}")
            return []