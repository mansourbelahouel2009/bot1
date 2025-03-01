import ccxt
import logging
from typing import Dict, Optional
from config import Config
from .mock_data import MockBinanceData

class BinanceClient:
    def __init__(self):
        self.client = None
        self.mock_data = MockBinanceData()
        self.use_mock = not (Config.API_KEY and Config.API_SECRET)
        self.initialize_client()

    def initialize_client(self) -> None:
        """Initialize Binance API client using ccxt or mock data"""
        try:
            if not self.use_mock:
                options = {
                    'apiKey': Config.API_KEY,
                    'secret': Config.API_SECRET,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot'
                    }
                }

                if Config.USE_TESTNET:
                    options['urls'] = {
                        'api': {
                            'public': 'https://testnet.binance.vision/api/v3',
                            'private': 'https://testnet.binance.vision/api/v3',
                        }
                    }
                    logging.info("Connecting to Binance Testnet")

                self.client = ccxt.binance(options)

                if Config.USE_TESTNET:
                    self.client.set_sandbox_mode(True)

                logging.info("Successfully connected to Binance API")
            else:
                logging.info("Using mock data for testing")

        except Exception as e:
            logging.error(f"Failed to connect to Binance API: {e}")
            self.use_mock = True
            logging.info("Falling back to mock data")

    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            if self.use_mock:
                return self.mock_data.get_mock_account()
            return self.client.fetch_balance()
        except Exception as e:
            logging.error(f"Failed to get account info: {e}")
            return self.mock_data.get_mock_account()

    def get_symbol_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            if self.use_mock:
                return self.mock_data.get_mock_price(symbol)
            ticker = self.client.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logging.error(f"Failed to get price for {symbol}: {e}")
            return self.mock_data.get_mock_price(symbol)

    def place_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a new order"""
        try:
            if self.use_mock:
                # Simulate successful order placement
                price = self.get_symbol_price(symbol)
                return {
                    'symbol': symbol,
                    'side': side,
                    'type': 'market',
                    'amount': quantity,
                    'price': price,
                    'status': 'closed'
                }

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
        """Fetch OHLCV data using ccxt or mock data"""
        try:
            if self.use_mock:
                return self.mock_data.get_mock_ohlcv(symbol, limit)

            ohlcv = self.client.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit
            )
            return ohlcv
        except Exception as e:
            logging.error(f"Failed to fetch OHLCV data: {e}")
            return self.mock_data.get_mock_ohlcv(symbol, limit)

    def get_24h_volume(self, symbol: str) -> float:
        """Get 24h trading volume for a symbol"""
        try:
            if self.use_mock:
                # Return mock volume above minimum threshold for testing
                return Config.MIN_VOLUME_24H * 2

            ticker = self.client.fetch_ticker(symbol)
            return float(ticker['quoteVolume'])
        except Exception as e:
            logging.error(f"Failed to get 24h volume for {symbol}: {e}")
            return 0