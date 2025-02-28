import logging
from src.connection.binance_client import BinanceClient
from src.config import Config

logging.basicConfig(level=logging.INFO)

def test_connection():
    try:
        # Initialize client
        client = BinanceClient()
        
        # Test market data
        symbol = "BTCUSDT"
        price = client.get_symbol_price(symbol)
        if price:
            logging.info(f"Successfully fetched {symbol} price: {price}")
        else:
            logging.error("Failed to fetch price")
            
        # Test historical data
        ohlcv = client.fetch_ohlcv(symbol, "1h", 10)
        if ohlcv:
            logging.info(f"Successfully fetched historical data: {len(ohlcv)} candles")
        else:
            logging.error("Failed to fetch historical data")
            
    except Exception as e:
        logging.error(f"Error testing connection: {e}")

if __name__ == "__main__":
    test_connection()
