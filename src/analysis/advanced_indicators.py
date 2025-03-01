import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, Tuple
import logging

class AdvancedIndicators:
    def __init__(self):
        self.trend_thresholds = {
            'strong_uptrend': 0.8,
            'uptrend': 0.6,
            'sideways': 0.4,
            'downtrend': 0.3
        }

    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """حساب جميع المؤشرات المتقدمة"""
        try:
            indicators = {}

            # المؤشرات الأساسية
            indicators.update(self._calculate_trend_strength(df))
            indicators.update(self._calculate_volatility(df))
            indicators.update(self._calculate_momentum(df))
            indicators.update(self._calculate_volume_analysis(df))

            # تحليل الاتجاه
            trend_analysis = self._analyze_market_trend(indicators)
            indicators.update(trend_analysis)

            return indicators

        except Exception as e:
            logging.error(f"خطأ في حساب المؤشرات: {e}")
            return {}

    def _calculate_trend_strength(self, df: pd.DataFrame) -> Dict:
        """حساب قوة الاتجاه"""
        try:
            # ADX - Average Directional Index
            adx = df.ta.adx()
            df['ADX'] = adx['ADX_14']
            df['DIplus'] = adx['DMP_14']
            df['DIminus'] = adx['DMN_14']

            # Moving Averages
            df['EMA_9'] = df.ta.ema(length=9)
            df['EMA_21'] = df.ta.ema(length=21)
            df['SMA_50'] = df.ta.sma(length=50)
            df['SMA_200'] = df.ta.sma(length=200)

            return {
                'adx': df['ADX'].iloc[-1],
                'di_plus': df['DIplus'].iloc[-1],
                'di_minus': df['DIminus'].iloc[-1]
            }

        except Exception as e:
            logging.error(f"خطأ في حساب قوة الاتجاه: {e}")
            return {}

    def _calculate_volatility(self, df: pd.DataFrame) -> Dict:
        """حساب التقلب"""
        try:
            # Bollinger Bands
            bbands = df.ta.bbands()
            df['BB_upper'] = bbands['BBU_20_2.0']
            df['BB_middle'] = bbands['BBM_20_2.0']
            df['BB_lower'] = bbands['BBL_20_2.0']

            # ATR - Average True Range
            df['ATR'] = df.ta.atr(length=14)

            # حساب التقلب النسبي
            df['volatility'] = (df['ATR'] / df['close']) * 100

            return {
                'atr': df['ATR'].iloc[-1],
                'bb_width': (df['BB_upper'].iloc[-1] - df['BB_lower'].iloc[-1]) / df['BB_middle'].iloc[-1],
                'volatility': df['volatility'].iloc[-1]
            }

        except Exception as e:
            logging.error(f"خطأ في حساب التقلب: {e}")
            return {}

    def _calculate_momentum(self, df: pd.DataFrame) -> Dict:
        """حساب الزخم"""
        try:
            # RSI
            df['RSI'] = df.ta.rsi(length=14)

            # MACD
            macd = df.ta.macd()
            df['MACD'] = macd['MACD_12_26_9']
            df['Signal'] = macd['MACDs_12_26_9']

            # Stochastic Oscillator
            stoch = df.ta.stoch()
            df['SO_K'] = stoch['STOCHk_14_3_3']
            df['SO_D'] = stoch['STOCHd_14_3_3']

            return {
                'rsi': df['RSI'].iloc[-1],
                'macd': df['MACD'].iloc[-1],
                'macd_signal': df['Signal'].iloc[-1],
                'stoch_k': df['SO_K'].iloc[-1],
                'stoch_d': df['SO_D'].iloc[-1]
            }

        except Exception as e:
            logging.error(f"خطأ في حساب الزخم: {e}")
            return {}

    def _calculate_volume_analysis(self, df: pd.DataFrame) -> Dict:
        """تحليل الحجم"""
        try:
            # On-Balance Volume
            df['OBV'] = df.ta.obv()

            # Volume Moving Average
            df['VOL_MA'] = df.ta.sma(close=df['volume'], length=20)

            # Money Flow Index
            df['MFI'] = df.ta.mfi()

            return {
                'obv': df['OBV'].iloc[-1],
                'volume_ma': df['VOL_MA'].iloc[-1],
                'mfi': df['MFI'].iloc[-1]
            }

        except Exception as e:
            logging.error(f"خطأ في تحليل الحجم: {e}")
            return {}

    def _analyze_market_trend(self, indicators: Dict) -> Dict:
        """تحليل اتجاه السوق"""
        try:
            trend_score = 0
            confidence = 0

            # تحليل ADX
            if indicators.get('adx', 0) > 25:
                if indicators.get('di_plus', 0) > indicators.get('di_minus', 0):
                    trend_score += 0.3
                else:
                    trend_score -= 0.3
                confidence += 0.2

            # تحليل RSI
            rsi = indicators.get('rsi', 50)
            if rsi > 70:
                trend_score -= 0.2
            elif rsi < 30:
                trend_score += 0.2
            confidence += 0.1

            # تحليل MACD
            if indicators.get('macd', 0) > indicators.get('macd_signal', 0):
                trend_score += 0.2
            else:
                trend_score -= 0.2
            confidence += 0.2

            # تحليل الحجم
            if indicators.get('mfi', 50) > 60:
                trend_score += 0.1
                confidence += 0.1

            # تحديد الاتجاه
            if trend_score > self.trend_thresholds['strong_uptrend']:
                trend = 'STRONG_UPTREND'
            elif trend_score > self.trend_thresholds['uptrend']:
                trend = 'UPTREND'
            elif trend_score < -self.trend_thresholds['strong_uptrend']:
                trend = 'STRONG_DOWNTREND'
            elif trend_score < -self.trend_thresholds['uptrend']:
                trend = 'DOWNTREND'
            else:
                trend = 'SIDEWAYS'

            return {
                'trend': trend,
                'trend_score': trend_score,
                'trend_confidence': min(confidence, 1.0)
            }

        except Exception as e:
            logging.error(f"خطأ في تحليل اتجاه السوق: {e}")
            return {
                'trend': 'UNKNOWN',
                'trend_score': 0,
                'trend_confidence': 0
            }