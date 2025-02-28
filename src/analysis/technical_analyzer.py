import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

class TechnicalAnalyzer:
    def __init__(self):
        self.signals = {}
        
    def analyze_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze technical indicators and generate signals"""
        try:
            signals = {
                'rsi_signal': self._analyze_rsi(df),
                'macd_signal': self._analyze_macd(df),
                'ma_signal': self._analyze_moving_averages(df)
            }
            
            # Combine signals
            combined_signal = np.mean([v for v in signals.values()])
            signals['combined_signal'] = combined_signal
            
            self.signals = signals
            return signals
            
        except Exception as e:
            logging.error(f"Error in technical analysis: {e}")
            return {}
            
    def _analyze_rsi(self, df: pd.DataFrame) -> float:
        """Analyze RSI indicator"""
        try:
            last_rsi = df['rsi'].iloc[-1]
            
            if last_rsi < 30:
                return 1  # Strong buy signal
            elif last_rsi > 70:
                return -1  # Strong sell signal
            else:
                return 0  # Neutral
                
        except Exception as e:
            logging.error(f"Error in RSI analysis: {e}")
            return 0
            
    def _analyze_macd(self, df: pd.DataFrame) -> float:
        """Analyze MACD indicator"""
        try:
            macd = df['macd'].iloc[-1]
            signal = df['macd_signal'].iloc[-1]
            
            if macd > signal:
                return 1  # Buy signal
            elif macd < signal:
                return -1  # Sell signal
            else:
                return 0  # Neutral
                
        except Exception as e:
            logging.error(f"Error in MACD analysis: {e}")
            return 0
            
    def _analyze_moving_averages(self, df: pd.DataFrame) -> float:
        """Analyze Moving Averages"""
        try:
            ma_20 = df['ma_20'].iloc[-1]
            ma_50 = df['ma_50'].iloc[-1]
            
            if ma_20 > ma_50:
                return 1  # Bullish trend
            elif ma_20 < ma_50:
                return -1  # Bearish trend
            else:
                return 0  # Neutral
                
        except Exception as e:
            logging.error(f"Error in Moving Averages analysis: {e}")
            return 0
