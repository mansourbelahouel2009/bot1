import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple
from src.connection.binance_client import BinanceClient
from src.config import Config
from src.database.models import DatabaseManager
import logging

class DataCollector:
    def __init__(self, binance_client: BinanceClient, db_manager: DatabaseManager):
        self.client = binance_client
        self.db_manager = db_manager
        self.symbol_data = {}

    def fetch_multiple_symbols(self, symbols: List[str], interval: str, limit: int = 500) -> Dict[str, pd.DataFrame]:
        """جلب البيانات التاريخية لعدة عملات"""
        results = {}
        for symbol in symbols:
            try:
                df = self.fetch_historical_data(symbol, interval, limit)
                if df is not None:
                    df = self.add_technical_indicators(df)
                    results[symbol] = df
                    # حفظ البيانات في قاعدة البيانات
                    self.db_manager.save_market_data(symbol, {
                        'data': df.to_dict(orient='records'),
                        'interval': interval,
                        'indicators': self._get_latest_indicators(df)
                    })
            except Exception as e:
                logging.error(f"خطأ في جلب بيانات {symbol}: {e}")
        return results

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
        """إضافة مؤشرات فنية متقدمة للبيانات"""
        try:
            # المؤشرات الأساسية
            df = self._add_trend_indicators(df)
            df = self._add_momentum_indicators(df)
            df = self._add_volatility_indicators(df)
            df = self._add_volume_indicators(df)

            # تحليل الاتجاه
            df = self._add_trend_analysis(df)

            return df

        except Exception as e:
            logging.error(f"خطأ في إضافة المؤشرات الفنية: {e}")
            return df

    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """إضافة مؤشرات الاتجاه"""
        # EMA
        df['ema_9'] = df['close'].ewm(span=9).mean()
        df['ema_21'] = df['close'].ewm(span=21).mean()
        df['ema_50'] = df['close'].ewm(span=50).mean()
        df['ema_200'] = df['close'].ewm(span=200).mean()

        # Moving Averages
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()

        # ADX (Average Directional Index)
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift(1))
        df['tr3'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()

        return df

    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """إضافة مؤشرات الزخم"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # Stochastic Oscillator
        df['k_line'] = ((df['close'] - df['low'].rolling(window=14).min()) / 
                       (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min())) * 100
        df['d_line'] = df['k_line'].rolling(window=3).mean()

        return df

    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """إضافة مؤشرات التقلب"""
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_upper'] = df['bb_middle'] + 2 * df['close'].rolling(window=20).std()
        df['bb_lower'] = df['bb_middle'] - 2 * df['close'].rolling(window=20).std()

        # Average True Range (ATR)
        df['atr'] = df['tr'].rolling(window=14).mean()

        # Volatility Index
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean() * 100

        return df

    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """إضافة مؤشرات الحجم"""
        # On-Balance Volume (OBV)
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).cumsum()

        # Volume Moving Average
        df['volume_ma'] = df['volume'].rolling(window=20).mean()

        # Chaikin Money Flow
        mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        mfv = mfm * df['volume']
        df['cmf'] = mfv.rolling(window=20).sum() / df['volume'].rolling(window=20).sum()

        return df

    def _add_trend_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """تحليل وتحديد اتجاه السوق"""
        # حساب قوة الاتجاه
        df['trend_strength'] = np.where(
            df['ema_9'] > df['ema_21'],
            np.where(df['ema_21'] > df['ema_50'], 2, 1),
            np.where(df['ema_21'] < df['ema_50'], -2, -1)
        )

        # تحديد نوع الاتجاه
        df['trend_type'] = np.where(
            df['trend_strength'].abs() == 2,
            np.where(df['trend_strength'] > 0, 'STRONG_UPTREND', 'STRONG_DOWNTREND'),
            np.where(df['trend_strength'] > 0, 'UPTREND', 'DOWNTREND')
        )

        # حساب تقلب السوق
        df['market_volatility'] = df['volatility'].rolling(window=20).mean()

        # تحديد حالة السوق
        df['market_condition'] = np.where(
            df['market_volatility'] > df['market_volatility'].quantile(0.8),
            'VOLATILE',
            np.where(df['market_volatility'] < df['market_volatility'].quantile(0.2),
                    'STABLE', 'NORMAL')
        )

        return df

    def _get_latest_indicators(self, df: pd.DataFrame) -> Dict:
        """استخراج آخر قيم المؤشرات"""
        latest = df.iloc[-1]
        return {
            'trend': {
                'type': latest['trend_type'],
                'strength': latest['trend_strength'],
                'market_condition': latest['market_condition']
            },
            'momentum': {
                'rsi': latest['rsi'],
                'macd': latest['macd'],
                'macd_signal': latest['macd_signal'],
                'stoch_k': latest['k_line'],
                'stoch_d': latest['d_line']
            },
            'volatility': {
                'bb_upper': latest['bb_upper'],
                'bb_middle': latest['bb_middle'],
                'bb_lower': latest['bb_lower'],
                'atr': latest['atr'],
                'volatility_index': latest['volatility']
            },
            'volume': {
                'current': latest['volume'],
                'ma': latest['volume_ma'],
                'cmf': latest['cmf'],
                'obv': latest['obv']
            }
        }