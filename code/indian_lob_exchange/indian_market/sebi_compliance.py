"""
Integrates all SEBI regulatory components into a single engine.
"""
from datetime import time
from typing import Optional, Tuple
from ..core.orders import Order
from .trading_sessions import TradingSessionManager
from .circuit_breakers import CircuitBreakerMonitor

class SEBIComplianceEngine:
    """
    A facade that enforces SEBI regulations before processing orders
    and after processing trades.
    """
    def __init__(self, reference_price: float, stock_category: str):
        self.session_manager = TradingSessionManager()
        self.circuit_breaker = CircuitBreakerMonitor(reference_price, stock_category)

    def validate_order(self, order: Order, current_time: time) -> Tuple[bool, str]:
        """
        Performs all pre-trade compliance checks on a new order.

        Args:
            order: The order to be validated.
            current_time: The current simulation time.
        
        Returns:
            A tuple (is_valid, reason_string).
        """
        # 1. Check if trading is halted
        if self.circuit_breaker.market_halted:
            # Add logic here to check if halt_end_time has passed
            return False, "Market is halted due to circuit breaker."

        # 2. Check trading session rules
        if not self.session_manager.is_order_allowed(order.order_type, current_time):
            session = self.session_manager.get_current_session(current_time)
            return False, f"{order.order_type.name} orders not allowed in {session} session."
            
        # 3. Check stock price band for limit orders
        if order.price and not self.circuit_breaker.check_price_band(order.price):
            return False, (f"Price {order.price} is outside the price band "
                           f"({self.circuit_breaker.lower_band:.2f} - {self.circuit_breaker.upper_band:.2f}).")
            
        # Add more checks here (e.g., audit trails, tick size)

        return True, "Order is compliant."

    def post_trade_check(self, trade_price: float, current_time: time):
        """
        Performs post-trade checks, primarily for circuit breakers.
        """
        halt_info = self.circuit_breaker.check_index_circuit_breaker(trade_price, current_time)
        if halt_info["triggered"]:
            print(f"CIRCUIT BREAKER TRIGGERED: {halt_info}")
            # Here you would implement the logic to halt the market
            # self.circuit_breaker.market_halted = True
            # ... set halt_end_time ...
        
        # Add logic for audit trail generation here
