import pandas as pd
import numpy as np
from typing import Optional
from src.connection.binance_client import BinanceClient
from src.config import Config
import logging

class DataCollector:
    def __init__(self, binance_client: BinanceClient):
        self.client = binance_client

    def fetch_historical_data(self, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        """Fetch historical kline data from Binance using ccxt"""
        try:
            ohlcv = self.client.fetch_ohlcv(symbol, interval, limit)

            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])

            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_columns] = df[numeric_columns].astype(float)

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            logging.error(f"Error fetching historical data: {e}")
            return None

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        try:
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=Config.TECHNICAL_PARAMS['rsi_period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=Config.TECHNICAL_PARAMS['rsi_period']).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # Moving averages
            df['ma_20'] = df['close'].rolling(window=Config.TECHNICAL_PARAMS['ma_short']).mean()
            df['ma_50'] = df['close'].rolling(window=Config.TECHNICAL_PARAMS['ma_long']).mean()

            # MACD
            exp1 = df['close'].ewm(span=Config.TECHNICAL_PARAMS['macd_fast']).mean()
            exp2 = df['close'].ewm(span=Config.TECHNICAL_PARAMS['macd_slow']).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=Config.TECHNICAL_PARAMS['macd_signal']).mean()

            return df

        except Exception as e:
            logging.error(f"Error adding technical indicators: {e}")
            return df