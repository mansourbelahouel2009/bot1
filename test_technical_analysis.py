import logging
from src.connection.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_analyzer import TechnicalAnalyzer

logging.basicConfig(level=logging.INFO)

def test_technical_analysis():
    try:
        # Initialize components
        client = BinanceClient()
        data_collector = DataCollector(client)
        analyzer = TechnicalAnalyzer()
        
        # Get test data
        symbol = "BTCUSDT"
        df = data_collector.fetch_historical_data(symbol, "1h")
        
        if df is not None:
            # Add technical indicators
            df = data_collector.add_technical_indicators(df)
            
            # Analyze indicators
            signals = analyzer.analyze_indicators(df)
            
            # Log results
            logging.info("Technical Analysis Results:")
            logging.info(f"RSI Signal: {signals['rsi_signal']}")
            logging.info(f"MACD Signal: {signals['macd_signal']}")
            logging.info(f"MA Signal: {signals['ma_signal']}")
            logging.info(f"Combined Signal: {signals['combined_signal']}")
            
            # Verify indicators were calculated
            logging.info("\nIndicator Values (last row):")
            logging.info(f"RSI: {df['rsi'].iloc[-1]:.2f}")
            logging.info(f"MACD: {df['macd'].iloc[-1]:.2f}")
            logging.info(f"MA20: {df['ma_20'].iloc[-1]:.2f}")
            logging.info(f"MA50: {df['ma_50'].iloc[-1]:.2f}")
            
        else:
            logging.error("Failed to fetch historical data")
            
    except Exception as e:
        logging.error(f"Error in technical analysis test: {e}")

if __name__ == "__main__":
    test_technical_analysis()
