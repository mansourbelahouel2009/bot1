import logging
from src.connection.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_analyzer import TechnicalAnalyzer
from src.analysis.ml_analyzer import MLAnalyzer
from src.analysis.news_analyzer import NewsAnalyzer
from src.trading.strategy import TradingStrategy
from src.config import Config

logging.basicConfig(level=logging.INFO)

def test_trading_strategy():
    try:
        # Initialize components
        client = BinanceClient()
        data_collector = DataCollector(client)
        technical_analyzer = TechnicalAnalyzer()
        ml_analyzer = MLAnalyzer()
        news_analyzer = NewsAnalyzer()
        
        strategy = TradingStrategy(technical_analyzer, ml_analyzer, news_analyzer)
        
        # Get test data
        symbol = "BTCUSDT"
        df = data_collector.fetch_historical_data(symbol, "1h")
        
        if df is not None:
            # Add technical indicators
            df = data_collector.add_technical_indicators(df)
            
            # Get technical signals
            technical_signals = technical_analyzer.analyze_indicators(df)
            
            # Get current price from mock data
            current_price = client.get_symbol_price(symbol)
            
            # Generate trading signal
            signal = strategy.generate_signal(
                technical_signals=technical_signals,
                ml_prediction=None,  # Skip ML prediction for now
                current_price=current_price,
                symbol=symbol
            )
            
            # Log results
            logging.info("\nTrading Strategy Results:")
            logging.info(f"Signal Strength: {signal['signal']}")
            logging.info(f"Recommended Action: {signal['action']}")
            logging.info(f"Confidence Level: {signal['confidence']}")
            logging.info(f"News Sentiment: {signal['news_sentiment']}")
            
            # Test position size calculation
            available_balance = 10000  # Mock balance
            position_size = strategy.calculate_position_size(
                available_balance=available_balance,
                signal_confidence=signal['confidence']
            )
            logging.info(f"\nPosition Sizing:")
            logging.info(f"Available Balance: {available_balance} USDT")
            logging.info(f"Recommended Position Size: {position_size} USDT")
            
        else:
            logging.error("Failed to fetch historical data")
            
    except Exception as e:
        logging.error(f"Error in trading strategy test: {e}")

if __name__ == "__main__":
    test_trading_strategy()
