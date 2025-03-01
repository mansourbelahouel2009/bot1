import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging
from scipy import stats

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
            df['TR'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            df['DMplus'] = np.where(
                (df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                np.maximum(df['high'] - df['high'].shift(1), 0),
                0
            )
            df['DMminus'] = np.where(
                (df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                np.maximum(df['low'].shift(1) - df['low'], 0),
                0
            )
            
            # حساب المتوسطات المتحركة
            period = 14
            df['TR_MA'] = df['TR'].rolling(window=period).mean()
            df['DMplus_MA'] = df['DMplus'].rolling(window=period).mean()
            df['DMminus_MA'] = df['DMminus'].rolling(window=period).mean()
            
            # حساب ADX
            df['DIplus'] = 100 * (df['DMplus_MA'] / df['TR_MA'])
            df['DIminus'] = 100 * (df['DMminus_MA'] / df['TR_MA'])
            df['DX'] = 100 * abs(df['DIplus'] - df['DIminus']) / (df['DIplus'] + df['DIminus'])
            df['ADX'] = df['DX'].rolling(window=period).mean()
            
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
            # ATR - Average True Range
            period = 14
            df['ATR'] = df['TR'].rolling(window=period).mean()
            
            # Bollinger Bands
            df['BB_middle'] = df['close'].rolling(window=20).mean()
            df['BB_upper'] = df['BB_middle'] + 2 * df['close'].rolling(window=20).std()
            df['BB_lower'] = df['BB_middle'] - 2 * df['close'].rolling(window=20).std()
            
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
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            # Stochastic Oscillator
            period = 14
            df['SO_K'] = 100 * (df['close'] - df['low'].rolling(window=period).min()) / \
                        (df['high'].rolling(window=period).max() - df['low'].rolling(window=period).min())
            df['SO_D'] = df['SO_K'].rolling(window=3).mean()
            
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
            # حساب مؤشر تدفق الأموال
            df['MFI'] = df['close'] * df['volume']
            df['MFI_MA'] = df['MFI'].rolling(window=14).mean()
            
            # تحليل تركيز الحجم
            df['VOL_MA'] = df['volume'].rolling(window=20).mean()
            volume_trend = (df['volume'].iloc[-1] / df['VOL_MA'].iloc[-1]) - 1
            
            return {
                'money_flow': df['MFI'].iloc[-1],
                'volume_trend': volume_trend,
                'volume_ma': df['VOL_MA'].iloc[-1]
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
            if indicators.get('volume_trend', 0) > 0.1:
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
