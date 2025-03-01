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
            self.technical_analysis.create_index([("symbol", 1), ("timestamp", -1)])
            self.news_analysis.create_index([("symbol", 1), ("timestamp", -1)])

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
        """حفظ بيانات السوق مع المؤشرات الفنية"""
        try:
            market_data = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'data': data['data'],
                'technical_indicators': {
                    'trend': {
                        'direction': data.get('market_trend', 'UNKNOWN'),
                        'strength': data.get('trend_strength', 0),
                        'confidence': data.get('trend_confidence', 0)
                    },
                    'moving_averages': {
                        'ema_9': data.get('EMA_9', 0),
                        'ema_21': data.get('EMA_21', 0),
                        'sma_50': data.get('SMA_50', 0),
                        'sma_200': data.get('SMA_200', 0)
                    },
                    'momentum': {
                        'rsi': data.get('RSI', 0),
                        'macd': data.get('MACD', 0),
                        'macd_signal': data.get('MACD_Signal', 0)
                    },
                    'volume': {
                        'current': data.get('volume', 0),
                        'ma': data.get('Volume_MA', 0),
                        'mfi': data.get('MFI', 0),
                        'obv': data.get('OBV', 0)
                    }
                }
            }

            if isinstance(self.market_data, list):
                self.market_data.append(market_data)
            else:
                self.market_data.insert_one(market_data)
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
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': trade_data.get('symbol'),
                'side': trade_data.get('side'),
                'price': trade_data.get('price'),
                'quantity': trade_data.get('quantity'),
                'total': trade_data.get('price', 0) * trade_data.get('quantity', 0),
                'status': trade_data.get('status'),
                'market_trend': trade_data.get('market_trend'),
                'strategy_type': trade_data.get('strategy_type')
            }

            if isinstance(self.trades, list):
                self.trades.append(trade_record)
            else:
                self.trades.insert_one(trade_record)
        except Exception as e:
            logging.error(f"خطأ في حفظ معلومات التداول: {e}")

    def get_recent_market_data(self, symbol: str, limit: int = 100) -> List[Dict]:
        """استرجاع أحدث بيانات السوق"""
        try:
            if isinstance(self.market_data, list):
                return sorted([item for item in self.market_data if item.get('symbol') == symbol], 
                            key=lambda x: x['timestamp'], reverse=True)[:limit]
            return list(self.market_data.find(
                {'symbol': symbol},
                {'_id': 0}
            ).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logging.error(f"خطأ في استرجاع بيانات السوق: {e}")
            return []

    def get_latest_technical_analysis(self, symbol: str) -> Optional[Dict]:
        """استرجاع آخر تحليل فني مع اتجاه السوق"""
        try:
            if isinstance(self.market_data, list):
                items = [item for item in self.market_data if item.get('symbol') == symbol]
                return items[0]['technical_indicators'] if items else None

            latest_data = self.market_data.find_one(
                {'symbol': symbol},
                {'_id': 0, 'technical_indicators': 1}
            )
            return latest_data.get('technical_indicators') if latest_data else None

        except Exception as e:
            logging.error(f"خطأ في استرجاع التحليل الفني: {e}")
            return None

    def get_market_trend(self, symbol: str) -> Optional[Dict]:
        """استرجاع اتجاه السوق الحالي"""
        try:
            analysis = self.get_latest_technical_analysis(symbol)
            return analysis.get('trend') if analysis else None
        except Exception as e:
            logging.error(f"خطأ في استرجاع اتجاه السوق: {e}")
            return None

    def get_trades_report(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """استرجاع تقرير التداولات"""
        try:
            if isinstance(self.trades, list):
                return sorted([item for item in self.trades 
                             if start_date <= item.get('timestamp') <= end_date],
                            key=lambda x: x['timestamp'], reverse=True)
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