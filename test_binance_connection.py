import logging
from connection.binance_client import BinanceClient
from config import Config

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
            if len(ohlcv) > 0:
                logging.info(f"First candle data: Timestamp={ohlcv[0][0]}, Open={ohlcv[0][1]}, High={ohlcv[0][2]}")
        else:
            logging.error("Failed to fetch historical data")

        # Test account data
        account = client.get_account_info()
        if account:
            logging.info("Successfully fetched account information")
            if 'balances' in account:
                logging.info("Available balances:")
                for balance in account['balances']:
                    if float(balance.get('free', 0)) > 0:
                        logging.info(f"{balance.get('asset', '')}: {balance.get('free', 0)}")
        else:
            logging.error("Failed to fetch account information")

        # Test order placement (mock)
        order = client.place_order(symbol, "BUY", 0.01)
        if order:
            logging.info(f"Successfully placed test order: {order}")
        else:
            logging.error("Failed to place test order")

    except Exception as e:
        logging.error(f"Error testing connection: {e}")

if __name__ == "__main__":
    test_connection()