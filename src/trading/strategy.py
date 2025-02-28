from typing import Dict, Optional
import logging
from src.analysis.technical_analyzer import TechnicalAnalyzer
from src.analysis.ml_analyzer import MLAnalyzer
from src.analysis.news_analyzer import NewsAnalyzer
from src.config import Config

class TradingStrategy:
    def __init__(self, technical_analyzer: TechnicalAnalyzer, 
                 ml_analyzer: MLAnalyzer, news_analyzer: NewsAnalyzer):
        self.technical_analyzer = technical_analyzer
        self.ml_analyzer = ml_analyzer
        self.news_analyzer = news_analyzer

    def generate_signal(self, technical_signals: Dict[str, float], 
                       ml_prediction: Optional[float], 
                       current_price: float,
                       symbol: str) -> Dict:
        """Generate trading signal based on technical, ML and news analysis"""
        try:
            # Weights for combining signals
            TECHNICAL_WEIGHT = 0.4
            ML_WEIGHT = 0.3
            NEWS_WEIGHT = 0.3

            # Get combined technical signal
            tech_signal = technical_signals['combined_signal']

            # Calculate ML signal
            ml_signal = 0
            if ml_prediction is not None:
                price_change = (ml_prediction - current_price) / current_price
                ml_signal = 1 if price_change > Config.PROFIT_THRESHOLD else -1 if price_change < -Config.PROFIT_THRESHOLD else 0

            # Get news sentiment
            news_sentiment = self.news_analyzer.get_market_sentiment(symbol)
            news_signal = news_sentiment['sentiment_score']

            # Combine signals
            final_signal = (
                tech_signal * TECHNICAL_WEIGHT + 
                ml_signal * ML_WEIGHT +
                news_signal * NEWS_WEIGHT
            )

            return {
                'signal': final_signal,
                'action': self._determine_action(final_signal),
                'confidence': abs(final_signal),
                'predicted_price': ml_prediction,
                'news_sentiment': news_sentiment['sentiment']
            }

        except Exception as e:
            logging.error(f"Error generating trading signal: {e}")
            return {
                'signal': 0, 
                'action': 'HOLD', 
                'confidence': 0, 
                'predicted_price': None,
                'news_sentiment': 'NEUTRAL'
            }

    def _determine_action(self, signal: float) -> str:
        """Determine trading action based on signal strength"""
        if signal > 0.5:
            return 'BUY'
        elif signal < -0.5:
            return 'SELL'
        else:
            return 'HOLD'

    def calculate_position_size(self, available_balance: float, 
                              signal_confidence: float) -> float:
        """Calculate position size based on signal confidence"""
        try:
            base_position = available_balance * Config.MAX_POSITION_SIZE
            position_size = base_position * signal_confidence
            return min(position_size, base_position)

        except Exception as e:
            logging.error(f"Error calculating position size: {e}")
            return 0