import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
from connection.binance_client import BinanceClient
from config import Config
from database.models import DatabaseManager
import logging
import pandas_ta as ta

class DataCollector:
    def __init__(self, binance_client: BinanceClient, db_manager: DatabaseManager):
        self.client = binance_client
        self.db_manager = db_manager
        self.symbol_data = {}
        self.trend_thresholds = {
            'strong_uptrend': 0.8,
            'uptrend': 0.6,
            'sideways': 0.4,
            'downtrend': 0.3
        }

    def fetch_multiple_symbols(self, symbols: List[str], interval: str, limit: int = 500) -> Dict[str, pd.DataFrame]:
        """جلب البيانات التاريخية لعدة عملات باستخدام threading"""
        try:
            # استخدام ThreadPoolExecutor لجلب البيانات بشكل متوازي
            with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
                # تنفيذ عمليات الجلب بشكل متوازي
                future_to_symbol = {
                    executor.submit(self.fetch_historical_data, symbol, interval, limit): symbol 
                    for symbol in symbols
                }

                results = {}
                for future in future_to_symbol:
                    symbol = future_to_symbol[future]
                    try:
                        df = future.result()
                        if df is not None:
                            # إضافة المؤشرات الفنية وتحليل الاتجاه
                            df = self.add_technical_indicators(df)
                            df = self.analyze_market_trend(df)
                            results[symbol] = df

                            # حفظ البيانات في قاعدة البيانات
                            self.db_manager.save_market_data(symbol, {
                                'data': df.to_dict(orient='records'),
                                'interval': interval,
                                'indicators': self._get_latest_indicators(df)
                            })
                            logging.info(f"تم جلب وتحليل بيانات {symbol} بنجاح")
                    except Exception as e:
                        logging.error(f"خطأ في جلب بيانات {symbol}: {e}")

                return results

        except Exception as e:
            logging.error(f"خطأ في جلب البيانات المتعددة: {e}")
            return {}

    def fetch_historical_data(self, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """جلب البيانات التاريخية من Binance"""
        try:
            ohlcv = self.client.fetch_ohlcv(symbol, interval, limit)

            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])

            # تحويل البيانات الرقمية
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_columns] = df[numeric_columns].astype(float)

            # تحويل الطابع الزمني
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            logging.error(f"خطأ في جلب البيانات التاريخية: {e}")
            return None

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """إضافة المؤشرات الفنية المتقدمة"""
        try:
            # ADX - Average Directional Index
            adx = df.ta.adx()
            df['ADX'] = adx['ADX_14']
            df['DIplus'] = adx['DMP_14']
            df['DIminus'] = adx['DMN_14']

            # المتوسطات المتحركة
            df['EMA_9'] = df.ta.ema(length=9)
            df['EMA_21'] = df.ta.ema(length=21)
            df['SMA_50'] = df.ta.sma(length=50)
            df['SMA_200'] = df.ta.sma(length=200)

            # RSI
            df['RSI'] = df.ta.rsi(length=14)

            # MACD
            macd = df.ta.macd()
            df['MACD'] = macd['MACD_12_26_9']
            df['MACD_Signal'] = macd['MACDs_12_26_9']

            # Bollinger Bands
            bbands = df.ta.bbands()
            df['BB_upper'] = bbands['BBU_20_2.0']
            df['BB_middle'] = bbands['BBM_20_2.0']
            df['BB_lower'] = bbands['BBL_20_2.0']

            # حجم التداول
            df['Volume_MA'] = df.ta.sma(close=df['volume'], length=20)
            df['OBV'] = df.ta.obv()
            df['MFI'] = df.ta.mfi()

            return df

        except Exception as e:
            logging.error(f"خطأ في إضافة المؤشرات الفنية: {e}")
            return df

    def analyze_market_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """تحليل وتحديد اتجاه السوق"""
        try:
            # حساب قوة الاتجاه
            trend_strength = np.zeros(len(df))
            confidence = np.zeros(len(df))

            for i in range(len(df)):
                # تحليل ADX
                if df['ADX'].iloc[i] > 25:
                    if df['DIplus'].iloc[i] > df['DIminus'].iloc[i]:
                        trend_strength[i] += 0.3
                    else:
                        trend_strength[i] -= 0.3
                    confidence[i] += 0.2

                # تحليل RSI
                rsi = df['RSI'].iloc[i]
                if rsi > 70:
                    trend_strength[i] -= 0.2
                elif rsi < 30:
                    trend_strength[i] += 0.2
                confidence[i] += 0.1

                # تحليل MACD
                if df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i]:
                    trend_strength[i] += 0.2
                else:
                    trend_strength[i] -= 0.2
                confidence[i] += 0.2

                # تحليل المتوسطات المتحركة
                if df['EMA_9'].iloc[i] > df['EMA_21'].iloc[i] > df['SMA_50'].iloc[i]:
                    trend_strength[i] += 0.2
                elif df['EMA_9'].iloc[i] < df['EMA_21'].iloc[i] < df['SMA_50'].iloc[i]:
                    trend_strength[i] -= 0.2
                confidence[i] += 0.1

            # تحديد الاتجاه
            df['trend_strength'] = trend_strength
            df['trend_confidence'] = confidence
            df['market_trend'] = pd.cut(
                trend_strength,
                bins=[-np.inf, -self.trend_thresholds['strong_uptrend'],
                      -self.trend_thresholds['uptrend'],
                      self.trend_thresholds['uptrend'],
                      self.trend_thresholds['strong_uptrend'], np.inf],
                labels=['STRONG_DOWNTREND', 'DOWNTREND', 'SIDEWAYS',
                       'UPTREND', 'STRONG_UPTREND']
            )

            return df

        except Exception as e:
            logging.error(f"خطأ في تحليل اتجاه السوق: {e}")
            return df

    def _get_latest_indicators(self, df: pd.DataFrame) -> Dict:
        """استخراج آخر قيم المؤشرات"""
        try:
            latest = df.iloc[-1]
            return {
                'trend': {
                    'direction': latest['market_trend'],
                    'strength': latest['trend_strength'],
                    'confidence': latest['trend_confidence']
                },
                'technical': {
                    'adx': latest['ADX'],
                    'rsi': latest['RSI'],
                    'macd': latest['MACD'],
                    'macd_signal': latest['MACD_Signal']
                },
                'moving_averages': {
                    'ema_9': latest['EMA_9'],
                    'ema_21': latest['EMA_21'],
                    'sma_50': latest['SMA_50'],
                    'sma_200': latest['SMA_200']
                },
                'volume': {
                    'current': latest['volume'],
                    'ma': latest['Volume_MA'],
                    'mfi': latest['MFI'],
                    'obv': latest['OBV']
                }
            }
        except Exception as e:
            logging.error(f"خطأ في استخراج المؤشرات: {e}")
            return {}