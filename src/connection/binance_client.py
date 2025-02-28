import ccxt
import logging
from typing import Dict, Optional
from src.config import Config

class BinanceClient:
    def __init__(self):
        self.client = None
        self.initialize_client()

    def initialize_client(self) -> None:
        """Initialize Binance API client using ccxt"""
        try:
            self.client = ccxt.binance({
                'apiKey': Config.API_KEY,
                'secret': Config.API_SECRET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })
            logging.info("Successfully connected to Binance API using ccxt")
        except Exception as e:
            logging.error(f"Failed to connect to Binance API: {e}")
            raise

    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            return self.client.fetch_balance()
        except Exception as e:
            logging.error(f"Failed to get account info: {e}")
            return {}

    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = self.client.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logging.error(f"Failed to get price for {symbol}: {e}")
            return None

    def place_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a new order"""
        try:
            order = self.client.create_order(
                symbol=symbol,
                type='market',
                side=side.lower(),
                amount=quantity
            )
            logging.info(f"Order placed successfully: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place order: {e}")
            return {}

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> list:
        """Fetch OHLCV data using ccxt"""
        try:
            ohlcv = self.client.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            return ohlcv
        except Exception as e:
            logging.error(f"Failed to fetch OHLCV data: {e}")
            return []