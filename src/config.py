import os
from typing import Dict, List

class Config:
    # Binance API credentials
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    API_SECRET = os.getenv('BINANCE_API_SECRET', '')

    # Use Binance Testnet
    USE_TESTNET = True

    # News API credentials
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

    # Trading parameters
    TRADING_PAIRS: List[str] = [
        'BTCUSDT',  # Bitcoin
        'ETHUSDT',  # Ethereum
        'BNBUSDT',  # Binance Coin
        'ADAUSDT',  # Cardano
        'DOGEUSDT', # Dogecoin
        'XRPUSDT',  # Ripple
        'DOTUSDT',  # Polkadot
        'UNIUSDT',  # Uniswap
        'LINKUSDT', # Chainlink
        'MATICUSDT' # Polygon
    ]
    TIMEFRAME: str = '1h'

    # Trading limits per currency
    MAX_CURRENCIES_TRADED: int = 5  # Maximum number of simultaneous positions
    MIN_VOLUME_24H: float = 1000000  # Minimum 24h volume in USDT

    # ML model parameters
    FEATURE_COLUMNS: List[str] = ['close', 'volume', 'rsi', 'macd', 'ma_20', 'ma_50']
    PREDICTION_WINDOW: int = 24

    # Trading thresholds
    PROFIT_THRESHOLD: float = 0.02  # 2%
    STOP_LOSS: float = 0.01  # 1%

    # Risk management
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio per currency
    MAX_TOTAL_POSITION: float = 0.5  # 50% of portfolio total

    # Technical indicators parameters
    TECHNICAL_PARAMS: Dict = {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'ma_short': 20,
        'ma_long': 50
    }

    # News analysis parameters
    NEWS_UPDATE_INTERVAL: int = 3600  # 1 hour in seconds
    NEWS_SENTIMENT_WEIGHT: float = 0.3  # Weight for news sentiment in trading decisions