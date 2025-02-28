import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
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
        """Build LSTM model"""
        try:
            self.model = Sequential([
                LSTM(50, return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            
            self.model.compile(optimizer='adam', loss='mse')
            logging.info("ML model built successfully")
            
        except Exception as e:
            logging.error(f"Error building model: {e}")
            
    def train_model(self, X: np.ndarray, y: np.ndarray, epochs: int = 50) -> None:
        """Train the ML model"""
        try:
            if self.model is None:
                self.build_model((X.shape[1], X.shape[2]))
                
            self.model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)
            logging.info("Model trained successfully")
            
        except Exception as e:
            logging.error(f"Error training model: {e}")
            
    def predict(self, data: pd.DataFrame) -> Optional[float]:
        """Make price prediction"""
        try:
            if self.model is None:
                raise ValueError("Model not trained")
                
            # Prepare prediction data
            features = data[Config.FEATURE_COLUMNS].values[-Config.PREDICTION_WINDOW:]
            scaled_features = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(np.array([scaled_features]))
            
            # Inverse transform prediction
            unscaled_prediction = self.scaler.inverse_transform(
                np.array([[prediction[0][0]] + [0] * (len(Config.FEATURE_COLUMNS)-1)])
            )[0][0]
            
            return unscaled_prediction
            
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return None
