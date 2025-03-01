import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Optional
import logging
from src.config import Config

class MLAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for ML model"""
        try:
            # Select features
            features = df[Config.FEATURE_COLUMNS].values

            # Scale features
            scaled_features = self.scaler.fit_transform(features)

            X, y = [], []
            for i in range(len(scaled_features) - Config.PREDICTION_WINDOW):
                X.append(scaled_features[i:i+Config.PREDICTION_WINDOW])
                y.append(scaled_features[i+Config.PREDICTION_WINDOW, 0])  # Predicting close price

            return np.array(X), np.array(y)

        except Exception as e:
            logging.error(f"Error preparing data: {e}")
            return np.array([]), np.array([])

    def build_model(self, input_shape: Tuple) -> None:
        """Build simple mock model"""
        logging.info("Using mock ML model for testing")
        self.model = "mock_model"

    def train_model(self, X: np.ndarray, y: np.ndarray, epochs: int = 50) -> None:
        """Train the mock ML model"""
        try:
            if self.model is None:
                self.build_model((X.shape[1], X.shape[2]))
            logging.info("Mock model training completed")

        except Exception as e:
            logging.error(f"Error training model: {e}")

    def predict(self, data: pd.DataFrame) -> Optional[float]:
        """Make mock price prediction"""
        try:
            if self.model is None:
                return None

            # Generate mock prediction (current price + small random change)
            current_price = data['close'].iloc[-1]
            prediction = current_price * (1 + np.random.uniform(-0.02, 0.02))

            return prediction

        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return None