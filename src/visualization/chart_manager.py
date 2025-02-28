import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf
from typing import Optional
import logging
import io
import base64

class ChartManager:
    def __init__(self):
        self.figures = {}
        
    def create_price_chart(self, df: pd.DataFrame, symbol: str) -> Optional[str]:
        """Create price chart with technical indicators"""
        try:
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # Plot price and moving averages
            ax1.plot(df.index, df['close'], label='Price', color='blue')
            ax1.plot(df.index, df['ma_20'], label='MA20', color='orange')
            ax1.plot(df.index, df['ma_50'], label='MA50', color='red')
            ax1.set_title(f'{symbol} Price Chart')
            ax1.legend()
            ax1.grid(True)
            
            # Plot RSI
            ax2.plot(df.index, df['rsi'], label='RSI', color='purple')
            ax2.axhline(y=70, color='r', linestyle='--')
            ax2.axhline(y=30, color='g', linestyle='--')
            ax2.set_title('RSI')
            ax2.legend()
            ax2.grid(True)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='svg')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            # Clear the current figure
            plt.close()
            
            # Encode to base64
            graphic = base64.b64encode(image_png).decode('utf-8')
            
            return graphic
            
        except Exception as e:
            logging.error(f"Error creating chart: {e}")
            return None
            
    def create_prediction_chart(self, historical_prices: pd.Series, 
                              predicted_price: float, 
                              symbol: str) -> Optional[str]:
        """Create prediction visualization chart"""
        try:
            plt.figure(figsize=(10, 6))
            
            # Plot historical prices
            plt.plot(historical_prices.index, historical_prices.values, 
                    label='Historical', color='blue')
            
            # Plot predicted price
            last_date = historical_prices.index[-1]
            plt.scatter(last_date, predicted_price, color='red', 
                       label='Prediction', s=100)
            
            plt.title(f'{symbol} Price Prediction')
            plt.legend()
            plt.grid(True)
            
            # Convert plot to base64 string
            buffer = io.BytesIO()
            plt.savefig(buffer, format='svg')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            # Clear the current figure
            plt.close()
            
            # Encode to base64
            graphic = base64.b64encode(image_png).decode('utf-8')
            
            return graphic
            
        except Exception as e:
            logging.error(f"Error creating prediction chart: {e}")
            return None
