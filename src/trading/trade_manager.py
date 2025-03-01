import logging
from typing import Dict, Optional
from datetime import datetime
from src.config import Config
from src.connection.binance_client import BinanceClient
from src.database.models import DatabaseManager

class TradeManager:
    def __init__(self, binance_client: BinanceClient, db_manager: DatabaseManager):
        self.client = binance_client
        self.db_manager = db_manager
        self.open_positions = {}

    def calculate_position_size(self, available_balance: float, signal_confidence: float) -> float:
        """حساب حجم المركز بناءً على الرصيد المتاح وقوة الإشارة"""
        try:
            # استخدام نسبة من الرصيد المتاح بناءً على قوة الإشارة
            max_position = available_balance * Config.MAX_POSITION_SIZE
            position_size = max_position * min(signal_confidence, 1.0)
            return position_size
        except Exception as e:
            logging.error(f"خطأ في حساب حجم المركز: {e}")
            return 0

    def calculate_entry_points(self, current_price: float, strategy_type: str) -> Dict:
        """حساب نقاط الدخول حسب نوع الاستراتيجية"""
        try:
            entry_points = {
                'limit_price': current_price,
                'stop_loss': current_price * (1 - Config.STOP_LOSS),
                'take_profit': current_price * (1 + Config.PROFIT_THRESHOLD)
            }

            if strategy_type == 'UPTREND':
                # زيادة نقطة الربح في الاتجاه الصاعد
                entry_points['take_profit'] = current_price * (1 + Config.PROFIT_THRESHOLD * 1.5)
            elif strategy_type == 'DOWNTREND':
                # تضييق وقف الخسارة في الاتجاه الهابط
                entry_points['stop_loss'] = current_price * (1 - Config.STOP_LOSS * 0.8)

            return entry_points
        except Exception as e:
            logging.error(f"خطأ في حساب نقاط الدخول: {e}")
            return {}

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict:
        """وضع أمر ليمت"""
        try:
            order = self.client.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                order_type='LIMIT'
            )

            if order:
                self.db_manager.save_trade({
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'type': 'LIMIT',
                    'status': order.get('status', 'NEW'),
                    'timestamp': datetime.now()
                })

            return order
        except Exception as e:
            logging.error(f"خطأ في وضع أمر ليمت: {e}")
            return {}

    def update_stop_loss(self, symbol: str, current_price: float, trailing_percentage: float = 0.01) -> Optional[float]:
        """تحديث الستوب لوز المتحرك"""
        try:
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                current_stop = position.get('stop_loss', 0)
                new_stop = current_price * (1 - trailing_percentage)

                if new_stop > current_stop:
                    self.open_positions[symbol]['stop_loss'] = new_stop
                    return new_stop

            return None
        except Exception as e:
            logging.error(f"خطأ في تحديث الستوب لوز: {e}")
            return None

    def check_exit_conditions(self, symbol: str, current_price: float) -> Dict:
        """التحقق من شروط الخروج"""
        try:
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                stop_loss = position.get('stop_loss', 0)
                take_profit = position.get('take_profit', float('inf'))

                if current_price <= stop_loss:
                    return {
                        'should_exit': True,
                        'reason': 'STOP_LOSS',
                        'price': current_price
                    }
                elif current_price >= take_profit:
                    return {
                        'should_exit': True,
                        'reason': 'TAKE_PROFIT',
                        'price': current_price
                    }

            return {'should_exit': False}
        except Exception as e:
            logging.error(f"خطأ في التحقق من شروط الخروج: {e}")
            return {'should_exit': False}

    def execute_market_exit(self, symbol: str, quantity: float, reason: str) -> Dict:
        """تنفيذ أمر خروج فوري"""
        try:
            order = self.client.place_order(
                symbol=symbol,
                side='SELL',
                quantity=quantity
            )

            if order:
                trade_data = {
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': quantity,
                    'price': order.get('price', 0),
                    'type': 'MARKET',
                    'reason': reason,
                    'status': order.get('status', 'FILLED'),
                    'timestamp': datetime.now()
                }
                self.db_manager.save_trade(trade_data)
                
                if symbol in self.open_positions:
                    del self.open_positions[symbol]

            return order
        except Exception as e:
            logging.error(f"خطأ في تنفيذ أمر الخروج: {e}")
            return {}
