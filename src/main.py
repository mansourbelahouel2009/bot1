import sys
import os
import logging
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connection.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_analyzer import TechnicalAnalyzer
from src.analysis.ml_analyzer import MLAnalyzer
from src.analysis.news_analyzer import NewsAnalyzer
from src.trading.strategy import TradingStrategy
from src.trading.trader import Trader
from src.visualization.chart_manager import ChartManager
from src.config import Config

logging.basicConfig(level=logging.INFO)

class TradingBot:
    def __init__(self):
        self.binance_client = BinanceClient()
        self.data_collector = DataCollector(self.binance_client)
        self.technical_analyzer = TechnicalAnalyzer()
        self.ml_analyzer = MLAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.strategy = TradingStrategy(
            self.technical_analyzer, 
            self.ml_analyzer,
            self.news_analyzer
        )
        self.trader = Trader(self.binance_client, self.strategy)
        self.chart_manager = ChartManager()

    def initialize(self):
        """Initialize the trading bot"""
        logging.info("Initializing trading bot...")

        # Train ML model with historical data
        for symbol in Config.TRADING_PAIRS:
            df = self.data_collector.fetch_historical_data(
                symbol, Config.TIMEFRAME
            )
            if df is not None:
                df = self.data_collector.add_technical_indicators(df)
                X, y = self.ml_analyzer.prepare_data(df)
                self.ml_analyzer.train_model(X, y)

                # Initial news sentiment analysis
                self.news_analyzer.get_market_sentiment(symbol)

    def run(self):
        """Run the trading bot"""
        logging.info("Starting trading bot...")
        last_news_update = {}

        while True:
            try:
                for symbol in Config.TRADING_PAIRS:
                    current_time = time.time()

                    # Update news sentiment periodically
                    if (symbol not in last_news_update or 
                        current_time - last_news_update[symbol] >= Config.NEWS_UPDATE_INTERVAL):
                        self.news_analyzer.get_market_sentiment(symbol)
                        last_news_update[symbol] = current_time

                    # Collect latest data
                    df = self.data_collector.fetch_historical_data(
                        symbol, Config.TIMEFRAME
                    )

                    if df is not None:
                        # Add technical indicators
                        df = self.data_collector.add_technical_indicators(df)

                        # Get current price
                        current_price = self.binance_client.get_symbol_price(symbol)

                        if current_price:
                            # Generate technical signals
                            technical_signals = self.technical_analyzer.analyze_indicators(df)

                            # Generate ML prediction
                            ml_prediction = self.ml_analyzer.predict(df)

                            # Generate trading signal
                            signal = self.strategy.generate_signal(
                                technical_signals, ml_prediction, current_price, symbol
                            )

                            # Execute trade
                            trade_result = self.trader.execute_trade(symbol, signal)

                            if trade_result['success']:
                                logging.info(f"Trade executed for {symbol}: {trade_result}")

                            # Update charts
                            self.chart_manager.create_price_chart(df, symbol)
                            if ml_prediction:
                                self.chart_manager.create_prediction_chart(
                                    df['close'], ml_prediction, symbol
                                )

                    # Monitor positions
                    self.trader.monitor_positions()

                # Sleep to avoid API rate limits
                time.sleep(60)

            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.initialize()
    bot.run()