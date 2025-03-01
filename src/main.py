import sys
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
np.NaN = np.nan  # إصلاح مشكلة pandas_ta

from connection.binance_client import BinanceClient
from data.data_collector import DataCollector
from analysis.technical_analyzer import TechnicalAnalyzer
from analysis.ml_analyzer import MLAnalyzer
from analysis.news_analyzer import NewsAnalyzer
from trading.strategy import TradingStrategy
from trading.advanced_strategies import StrategySelector
from trading.trade_manager import TradeManager
from visualization.dashboard import Dashboard
from config import Config
from database.models import DatabaseManager

def setup_logging():
    """إعداد التسجيل"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('trading_bot.log')
        ]
    )

class TradingBot:
    def __init__(self):
        setup_logging()
        try:
            self.db_manager = DatabaseManager()
            self.binance_client = BinanceClient()
            self.data_collector = DataCollector(self.binance_client, self.db_manager)
            self.technical_analyzer = TechnicalAnalyzer()
            self.ml_analyzer = MLAnalyzer()
            self.news_analyzer = NewsAnalyzer()
            self.strategy = TradingStrategy(
                self.technical_analyzer, 
                self.ml_analyzer,
                self.news_analyzer
            )
            self.strategy_selector = StrategySelector()
            self.trade_manager = TradeManager(self.binance_client, self.db_manager)
            self.active_pairs = {pair: True for pair in Config.TRADING_PAIRS}
            self.ranked_pairs = []
            logging.info("تم تهيئة جميع المكونات بنجاح")
        except Exception as e:
            logging.error(f"خطأ في تهيئة النظام: {e}")
            raise

    def initialize(self):
        """تهيئة روبوت التداول"""
        logging.info("بدء تهيئة روبوت التداول...")
        try:
            # تصفية أزواج التداول بناءً على الحجم
            self._filter_trading_pairs()

            # تحليل العملات النشطة باستخدام Threading
            active_pairs = [pair for pair, active in self.active_pairs.items() if active]
            market_data = self.data_collector.fetch_multiple_symbols(
                active_pairs, Config.TIMEFRAME
            )

            # تدريب نموذج التعلم الآلي وتحليل الأخبار
            for symbol, df in market_data.items():
                try:
                    self.ml_analyzer.train_model(df)
                    self.news_analyzer.get_market_sentiment(symbol)
                    logging.info(f"تم تهيئة {symbol} بنجاح")
                except Exception as e:
                    logging.error(f"خطأ في تهيئة {symbol}: {e}")
                    self.active_pairs[symbol] = False

            # تحليل وترتيب العملات
            self.ranked_pairs = self.rank_trading_pairs()
            logging.info("تم تهيئة النظام بنجاح")

        except Exception as e:
            logging.error(f"خطأ في تهيئة النظام: {e}")
            raise

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
                            trade_result = self.trade_manager.execute_trade(
                                symbol=symbol,
                                signal=strategy_analysis
                            )

                            if trade_result['success']:
                                logging.info(f"تم تنفيذ التداول لـ {symbol}: {trade_result}")

                # مراقبة المراكز المفتوحة
                self.trade_manager.monitor_positions()

                # حفظ التقرير اليومي
                if self._should_generate_report():
                    self._generate_daily_report()

                # انتظار لتجنب تجاوز حدود API
                time.sleep(60)

            except Exception as e:
                logging.error(f"خطأ في الحلقة الرئيسية: {e}")
                time.sleep(60)

    def rank_trading_pairs(self):
        """ترتيب أزواج التداول حسب الفرص"""
        try:
            active_pairs = [pair for pair, active in self.active_pairs.items() if active]
            ranked_pairs = []

            for symbol in active_pairs:
                # جلب وتحليل البيانات
                df = self.data_collector.fetch_historical_data(symbol, Config.TIMEFRAME)
                if df is not None:
                    # تحليل السوق وتحديد الاستراتيجية المناسبة
                    strategy_analysis = self.strategy_selector.select_strategy(df)
                    ml_prediction = self.ml_analyzer.predict(df)
                    current_price = self.binance_client.get_symbol_price(symbol)

                    ranked_pairs.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'strategy_analysis': strategy_analysis,
                        'ml_prediction': ml_prediction,
                        'market_data': df
                    })

            # ترتيب العملات حسب قوة الإشارة
            ranked_pairs.sort(
                key=lambda x: x['strategy_analysis']['signal_strength'] 
                if x.get('strategy_analysis') else 0,
                reverse=True
            )

            return ranked_pairs
        except Exception as e:
            logging.error(f"خطأ في ترتيب العملات: {e}")
            return []

def run_dashboard():
    """تشغيل واجهة المستخدم"""
    try:
        logging.info("بدء تشغيل واجهة المستخدم")
        setup_logging()

        # تهيئة النظام
        bot = TradingBot()
        bot.initialize()
        if not bot.ranked_pairs:
            bot.ranked_pairs = bot.rank_trading_pairs()

        logging.info(f"تم تهيئة {len(bot.ranked_pairs)} من العملات")

        # تهيئة واجهة المستخدم
        import streamlit as st
        st.set_page_config(
            page_title="نظام التداول الآلي",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # تشغيل لوحة التحكم
        dashboard = Dashboard(bot.trade_manager)
        dashboard.render_main_page(bot.ranked_pairs)

    except Exception as e:
        logging.error(f"خطأ في تشغيل واجهة المستخدم: {e}")
        sys.exit(1)

def run_trading_bot():
    """تشغيل نظام التداول"""
    try:
        logging.info("بدء تشغيل نظام التداول")
        setup_logging()

        bot = TradingBot()
        bot.initialize()
        bot.run(automatic_trading=True)
    except Exception as e:
        logging.error(f"خطأ في تشغيل نظام التداول: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if "--dashboard" in sys.argv:
        run_dashboard()
    else:
        run_trading_bot()