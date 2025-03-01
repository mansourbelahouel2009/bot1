from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
import logging

class DatabaseManager:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
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
            raise

    def save_market_data(self, symbol: str, data: Dict) -> None:
        """حفظ بيانات السوق"""
        try:
            data['symbol'] = symbol
            data['timestamp'] = datetime.now()
            self.market_data.insert_one(data)
        except Exception as e:
            logging.error(f"خطأ في حفظ بيانات السوق: {e}")

    def save_technical_analysis(self, symbol: str, analysis: Dict) -> None:
        """حفظ نتائج التحليل الفني"""
        try:
            analysis['symbol'] = symbol
            analysis['timestamp'] = datetime.now()
            self.technical_analysis.insert_one(analysis)
        except Exception as e:
            logging.error(f"خطأ في حفظ التحليل الفني: {e}")

    def save_news_analysis(self, symbol: str, news_data: Dict) -> None:
        """حفظ تحليل الأخبار"""
        try:
            news_data['symbol'] = symbol
            news_data['timestamp'] = datetime.now()
            self.news_analysis.insert_one(news_data)
        except Exception as e:
            logging.error(f"خطأ في حفظ تحليل الأخبار: {e}")

    def save_trade(self, trade_data: Dict) -> None:
        """حفظ معلومات التداول"""
        try:
            trade_data['timestamp'] = datetime.now()
            self.trades.insert_one(trade_data)
        except Exception as e:
            logging.error(f"خطأ في حفظ معلومات التداول: {e}")

    def get_recent_market_data(self, symbol: str, limit: int = 100) -> List[Dict]:
        """استرجاع أحدث بيانات السوق"""
        try:
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
