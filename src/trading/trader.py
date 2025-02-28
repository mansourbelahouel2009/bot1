from typing import Dict
import logging
from src.connection.binance_client import BinanceClient
from src.trading.strategy import TradingStrategy
from src.config import Config

class Trader:
    def __init__(self, binance_client: BinanceClient, strategy: TradingStrategy):
        self.client = binance_client
        self.strategy = strategy
        self.positions = {}
        
    def execute_trade(self, symbol: str, signal: Dict) -> Dict:
        """Execute trade based on strategy signal"""
        try:
            # Get account balance
            account_info = self.client.get_account_info()
            available_balance = float(account_info.get('balances', [{'free': 0}])[0]['free'])
            
            # Get current position
            current_position = self.positions.get(symbol, 0)
            
            # Calculate position size
            position_size = self.strategy.calculate_position_size(
                available_balance, signal['confidence']
            )
            
            result = {
                'success': False,
                'action': 'HOLD',
                'quantity': 0,
                'price': 0
            }
            
            if signal['action'] == 'BUY' and current_position <= 0:
                # Execute buy order
                order = self.client.place_order(
                    symbol=symbol,
                    side='BUY',
                    quantity=position_size
                )
                if order:
                    self.positions[symbol] = position_size
                    result.update({
                        'success': True,
                        'action': 'BUY',
                        'quantity': position_size,
                        'price': float(order['price']) if 'price' in order else 0
                    })
                    
            elif signal['action'] == 'SELL' and current_position > 0:
                # Execute sell order
                order = self.client.place_order(
                    symbol=symbol,
                    side='SELL',
                    quantity=current_position
                )
                if order:
                    self.positions[symbol] = 0
                    result.update({
                        'success': True,
                        'action': 'SELL',
                        'quantity': current_position,
                        'price': float(order['price']) if 'price' in order else 0
                    })
                    
            return result
            
        except Exception as e:
            logging.error(f"Error executing trade: {e}")
            return {'success': False, 'action': 'HOLD', 'quantity': 0, 'price': 0}
            
    def monitor_positions(self) -> None:
        """Monitor open positions for stop loss"""
        try:
            for symbol, position in self.positions.items():
                if position > 0:
                    current_price = self.client.get_symbol_price(symbol)
                    if current_price:
                        # Check stop loss
                        if current_price < position * (1 - Config.STOP_LOSS):
                            self.execute_trade(symbol, {
                                'action': 'SELL',
                                'confidence': 1
                            })
                            
        except Exception as e:
            logging.error(f"Error monitoring positions: {e}")
