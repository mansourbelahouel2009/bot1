import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np
from src.config import Config

class BaseStrategy:
    def __init__(self):
        self.min_confidence = 0.6
        self.stop_loss = Config.STOP_LOSS
        self.profit_target = Config.PROFIT_THRESHOLD

    def calculate_entry_exit(self, df: pd.DataFrame) -> Dict:
        """حساب نقاط الدخول والخروج الأساسية"""
        try:
            current_price = df['close'].iloc[-1]
            return {
                'entry_price': current_price,
                'stop_loss': current_price * (1 - self.stop_loss),
                'profit_target': current_price * (1 + self.profit_target)
            }
        except Exception as e:
            logging.error(f"خطأ في حساب نقاط الدخول والخروج: {e}")
            return {}

class UptrendStrategy(BaseStrategy):
    """استراتيجية السوق الصاعد"""
    def analyze(self, df: pd.DataFrame) -> Dict:
        try:
            # تحليل المقاومة والاختراق
            high_levels = df['high'].rolling(window=20).max()
            resistance_level = high_levels.iloc[-1]
            
            # تحليل حجم التداول
            volume_trend = df['volume'] > df['volume_ma']
            strong_volume = volume_trend.iloc[-5:].sum() >= 3
            
            # تحليل الزخم
            momentum_signals = (
                df['rsi'].iloc[-1] > 50 and
                df['macd'].iloc[-1] > df['macd_signal'].iloc[-1] and
                df['ema_9'].iloc[-1] > df['ema_21'].iloc[-1]
            )

            # تحديد قوة الإشارة
            signal_strength = sum([
                strong_volume,
                momentum_signals,
                df['trend_strength'].iloc[-1] > 1
            ]) / 3

            entry_points = self.calculate_entry_exit(df)
            entry_points.update({
                'signal_strength': signal_strength,
                'resistance_level': resistance_level,
                'strategy_type': 'UPTREND'
            })

            return entry_points

        except Exception as e:
            logging.error(f"خطأ في تحليل السوق الصاعد: {e}")
            return {}

class DowntrendStrategy(BaseStrategy):
    """استراتيجية السوق الهابط"""
    def analyze(self, df: pd.DataFrame) -> Dict:
        try:
            # تحليل مستويات فيبوناتشي
            high = df['high'].max()
            low = df['low'].min()
            diff = high - low
            
            fib_levels = {
                '0.236': high - (diff * 0.236),
                '0.382': high - (diff * 0.382),
                '0.618': high - (diff * 0.618)
            }
            
            current_price = df['close'].iloc[-1]
            nearest_fib = min(fib_levels.values(), key=lambda x: abs(x - current_price))
            
            # تحليل الزخم الهابط
            bearish_momentum = (
                df['rsi'].iloc[-1] < 40 and
                df['macd'].iloc[-1] < df['macd_signal'].iloc[-1] and
                df['ema_9'].iloc[-1] < df['ema_21'].iloc[-1]
            )
            
            # تحليل حجم التداول
            volume_confirmation = df['volume'] > df['volume_ma']
            strong_volume = volume_confirmation.iloc[-5:].sum() >= 3

            # تحديد قوة الإشارة
            signal_strength = sum([
                strong_volume,
                bearish_momentum,
                df['trend_strength'].iloc[-1] < -1
            ]) / 3

            entry_points = self.calculate_entry_exit(df)
            entry_points.update({
                'signal_strength': signal_strength,
                'fib_levels': fib_levels,
                'nearest_fib': nearest_fib,
                'strategy_type': 'DOWNTREND'
            })

            return entry_points

        except Exception as e:
            logging.error(f"خطأ في تحليل السوق الهابط: {e}")
            return {}

class RangeStrategy(BaseStrategy):
    """استراتيجية السوق العرضي"""
    def analyze(self, df: pd.DataFrame) -> Dict:
        try:
            # تحديد النطاق
            recent_data = df.tail(20)
            range_high = recent_data['high'].max()
            range_low = recent_data['low'].min()
            range_mid = (range_high + range_low) / 2
            
            current_price = df['close'].iloc[-1]
            
            # تحليل حالة النطاق
            near_support = current_price <= range_low * 1.01
            near_resistance = current_price >= range_high * 0.99
            
            # تحليل تقلب السوق
            volatility_decreasing = df['volatility'].iloc[-1] < df['volatility'].rolling(window=10).mean().iloc[-1]
            
            # تحليل حجم التداول
            volume_pattern = df['volume'] < df['volume_ma']
            low_volume = volume_pattern.iloc[-5:].sum() >= 3

            # تحديد قوة الإشارة
            signal_strength = sum([
                low_volume,
                volatility_decreasing,
                abs(df['trend_strength'].iloc[-1]) < 1
            ]) / 3

            entry_points = self.calculate_entry_exit(df)
            entry_points.update({
                'signal_strength': signal_strength,
                'range_high': range_high,
                'range_low': range_low,
                'range_mid': range_mid,
                'near_support': near_support,
                'near_resistance': near_resistance,
                'strategy_type': 'RANGE'
            })

            return entry_points

        except Exception as e:
            logging.error(f"خطأ في تحليل السوق العرضي: {e}")
            return {}

class StrategySelector:
    """محدد الاستراتيجية المناسبة بناءً على حالة السوق"""
    def __init__(self):
        self.uptrend_strategy = UptrendStrategy()
        self.downtrend_strategy = DowntrendStrategy()
        self.range_strategy = RangeStrategy()

    def select_strategy(self, df: pd.DataFrame) -> Dict:
        try:
            market_condition = df['market_condition'].iloc[-1]
            trend_type = df['trend_type'].iloc[-1]
            
            if market_condition == 'VOLATILE':
                return None  # تجنب التداول في الأسواق شديدة التقلب
            
            if 'UPTREND' in trend_type:
                return self.uptrend_strategy.analyze(df)
            elif 'DOWNTREND' in trend_type:
                return self.downtrend_strategy.analyze(df)
            else:
                return self.range_strategy.analyze(df)

        except Exception as e:
            logging.error(f"خطأ في اختيار الاستراتيجية: {e}")
            return None
