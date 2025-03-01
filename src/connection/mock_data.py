import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MockBinanceData:
    def __init__(self):
        self.mock_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 3000.0
        }

        self.mock_balances = {
            'USDT': {'free': 10000.0, 'used': 0.0, 'total': 10000.0},
            'BTC': {'free': 1.0, 'used': 0.0, 'total': 1.0},
            'ETH': {'free': 10.0, 'used': 0.0, 'total': 10.0}
        }

    def get_mock_price(self, symbol: str) -> float:
        """Get mock current price for a symbol"""
        return self.mock_prices.get(symbol, 0.0)

    def get_mock_account(self) -> dict:
        """Get mock account information"""
        return {
            'balances': [
                {'asset': k, **v} for k, v in self.mock_balances.items()
            ]
        }

    def get_mock_ohlcv(self, symbol: str, limit: int = 500) -> list:
        """Generate mock OHLCV data"""
        base_price = self.mock_prices.get(symbol, 1000.0)
        timestamps = [
            int((datetime.now() - timedelta(hours=i)).timestamp() * 1000)
            for i in range(limit)
        ]

        # Generate mock prices with some randomness
        np.random.seed(42)  # For reproducibility
        prices = base_price + np.random.normal(0, base_price * 0.02, limit)

        # Create mock trend patterns
        trend = np.sin(np.linspace(0, 4*np.pi, limit)) * base_price * 0.1
        prices += trend

        ohlcv_data = []
        for i, timestamp in enumerate(timestamps):
            price = prices[i]
            ohlcv_data.append([
                timestamp,  # timestamp
                price * 0.99,  # open
                price * 1.01,  # high
                price * 0.98,  # low
                price,  # close
                1000.0 + np.random.normal(0, 100)  # volume
            ])

        return ohlcv_data