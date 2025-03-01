import sys
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_analyzer import TechnicalAnalyzer
from src.analysis.ml_analyzer import MLAnalyzer
from src.analysis.news_analyzer import NewsAnalyzer
from src.trading.strategy import TradingStrategy
from src.trading.trader import Trader
from src.trading.advanced_strategies import StrategySelector
from src.visualization.chart_manager import ChartManager
from src.config import Config
from src.database.models import DatabaseManager
from src.trading.trade_manager import TradeManager

logging.basicConfig(level=logging.INFO)

class TradingBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.binance_client = BinanceClient()
        self.data_collector = DataCollector(self.binance_client, self.db_manager)
        self.technical_analyzer = TechnicalAnalyzer()
        self.ml_analyzer = MLAnalyzer()
        self.news_analyzer = NewsAnalyzer(self.db_manager)  # Update to use database manager
        self.strategy = TradingStrategy(
            self.technical_analyzer, 
            self.ml_analyzer,
            self.news_analyzer
        )
        self.strategy_selector = StrategySelector()
        self.trade_manager = TradeManager(self.binance_client, self.db_manager)  # Add trade manager
        self.chart_manager = ChartManager()
        self.active_pairs: Dict[str, bool] = {pair: True for pair in Config.TRADING_PAIRS}
        self.executor = ThreadPoolExecutor(max_workers=len(Config.TRADING_PAIRS))
        self.ranked_pairs = []

    def initialize(self):
        """تهيئة روبوت التداول"""
        logging.info("بدء تهيئة روبوت التداول...")

        # تصفية أزواج التداول بناءً على الحجم
        self._filter_trading_pairs()

        # تحليل العملات النشطة
        active_pairs = [pair for pair, active in self.active_pairs.items() if active]
        market_data = self.data_collector.fetch_multiple_symbols(
            active_pairs, Config.TIMEFRAME
        )

        # تدريب نموذج التعلم الآلي وتحليل الأخبار
        for symbol, df in market_data.items():
            try:
                X, y = self.ml_analyzer.prepare_data(df)
                self.ml_analyzer.train_model(X, y)
                self.news_analyzer.get_market_sentiment(symbol)
                logging.info(f"تم تهيئة {symbol} بنجاح")
            except Exception as e:
                logging.error(f"خطأ في تهيئة {symbol}: {e}")
                self.active_pairs[symbol] = False

    def _filter_trading_pairs(self):
        """تصفية أزواج التداول بناءً على الحجم"""
        for symbol in Config.TRADING_PAIRS:
            try:
                volume_24h = self.binance_client.get_24h_volume(symbol)
                if volume_24h < Config.MIN_VOLUME_24H:
                    logging.warning(f"استبعاد {symbol} بسبب حجم التداول المنخفض: {volume_24h}")
                    self.active_pairs[symbol] = False
            except Exception as e:
                logging.error(f"خطأ في فحص حجم التداول لـ {symbol}: {e}")
                self.active_pairs[symbol] = False

    def _analyze_trading_pair(self, symbol: str) -> Dict:
        """تحليل زوج تداول واحد"""
        try:
            # جمع وتحليل البيانات
            df = self.data_collector.fetch_historical_data(symbol, Config.TIMEFRAME)
            if df is not None:
                df = self.data_collector.add_technical_indicators(df)

                # تحليل السوق وتحديد الاستراتيجية المناسبة
                strategy_analysis = self.strategy_selector.select_strategy(df)

                # توقع السعر باستخدام التعلم الآلي
                ml_prediction = self.ml_analyzer.predict(df)

                # تحليل الأخبار
                news_sentiment = self.news_analyzer.get_market_sentiment(symbol)

                current_price = self.binance_client.get_symbol_price(symbol)

                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'strategy_analysis': strategy_analysis,
                    'ml_prediction': ml_prediction,
                    'news_sentiment': news_sentiment,
                    'market_data': df
                }

        except Exception as e:
            logging.error(f"خطأ في تحليل {symbol}: {e}")
        return None

    def rank_trading_pairs(self) -> List[Dict]:
        """ترتيب أزواج التداول بناءً على فرص التداول"""
        analysis_results = []
        active_symbols = [pair for pair, active in self.active_pairs.items() if active]

        # تحليل متوازي لجميع العملات
        with ThreadPoolExecutor(max_workers=len(active_symbols)) as executor:
            analysis_results = list(filter(None, executor.map(self._analyze_trading_pair, active_symbols)))

        # ترتيب النتائج
        ranked_pairs = sorted(
            analysis_results,
            key=lambda x: (
                x['strategy_analysis']['signal_strength'] if x['strategy_analysis'] else 0,
                abs(x['news_sentiment']['sentiment_score']) if x['news_sentiment'] else 0
            ),
            reverse=True
        )

        self.ranked_pairs = ranked_pairs
        return ranked_pairs

    def run(self, automatic_trading: bool = True):
        """تشغيل روبوت التداول"""
        logging.info("بدء تشغيل روبوت التداول...")

        while True:
            try:
                # تحليل وترتيب العملات
                ranked_pairs = self.rank_trading_pairs()

                if automatic_trading:
                    # التداول الآلي
                    for analysis in ranked_pairs[:Config.MAX_CURRENCIES_TRADED]:
                        symbol = analysis['symbol']
                        strategy_analysis = analysis['strategy_analysis']

                        if strategy_analysis and strategy_analysis['signal_strength'] > 0.6:
                            trade_result = self.trade_manager.execute_trade( # Use TradeManager
                                symbol=symbol,
                                signal=strategy_analysis
                            )

                            if trade_result['success']:
                                logging.info(f"تم تنفيذ التداول لـ {symbol}: {trade_result}")

                                # تحديث الرسوم البيانية
                                self.chart_manager.create_price_chart(
                                    analysis['market_data'], symbol
                                )
                                if analysis['ml_prediction']:
                                    self.chart_manager.create_prediction_chart(
                                        analysis['market_data']['close'],
                                        analysis['ml_prediction'],
                                        symbol
                                    )

                # مراقبة المراكز المفتوحة
                self.trade_manager.monitor_positions() # Use TradeManager

                # حفظ التقرير اليومي
                if self._should_generate_report():
                    self._generate_daily_report()

                # انتظار لتجنب تجاوز حدود API
                time.sleep(60)

            except Exception as e:
                logging.error(f"خطأ في الحلقة الرئيسية: {e}")
                time.sleep(60)

    def _should_generate_report(self) -> bool:
        """التحقق مما إذا كان يجب إنشاء تقرير يومي"""
        current_hour = time.localtime().tm_hour
        return current_hour == 0  # إنشاء تقرير عند منتصف الليل

    def _generate_daily_report(self):
        """إنشاء تقرير يومي"""
        try:
            today = time.strftime('%Y-%m-%d')
            yesterday = time.strftime(
                '%Y-%m-%d',
                time.localtime(time.time() - 86400)
            )

            # جمع بيانات التداول
            trades = self.db_manager.get_trades_report(
                start_date=yesterday,
                end_date=today
            )

            if trades:
                total_profit = sum(trade['profit'] for trade in trades)
                win_trades = sum(1 for trade in trades if trade['profit'] > 0)
                total_trades = len(trades)

                report = {
                    'date': today,
                    'total_trades': total_trades,
                    'win_rate': (win_trades / total_trades) * 100 if total_trades > 0 else 0,
                    'total_profit': total_profit,
                    'trades': trades
                }

                # حفظ التقرير في قاعدة البيانات
                self.db_manager.save_trade({'report': report})
                logging.info(f"تم إنشاء التقرير اليومي: {report}")

        except Exception as e:
            logging.error(f"خطأ في إنشاء التقرير اليومي: {e}")

if __name__ == "__main__":
    bot = TradingBot()
    bot.initialize()
    bot.run(automatic_trading=True)  # يمكن تغييرها إلى False للتداول اليدوي