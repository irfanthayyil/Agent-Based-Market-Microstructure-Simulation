"""
The main Exchange class that orchestrates all components.
"""
from datetime import datetime
from typing import List, Tuple
from .core.orders import Order, OrderPool
from .core.order_book import OrderBook
from .core.matching_engine import MatchingEngine, Trade
from .indian_market.sebi_compliance import SEBIComplianceEngine

class Exchange:
    """
    The central exchange, managing the order book, matching, and compliance.
    """
    def __init__(self, reference_price: float, stock_category: str = 'default'):
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)
        self.compliance_engine = SEBIComplianceEngine(reference_price, stock_category)
        self.order_pool = OrderPool()
        self._order_id_counter = 0

    def _get_next_order_id(self) -> int:
        self._order_id_counter += 1
        return self._order_id_counter

    def _get_current_time(self) -> datetime:
        """In a real simulation, this would come from the simulation clock."""
        return datetime.now()

    def submit_order(self, agent_id: int, side, quantity: int, order_type, 
                     price: float = None, trigger_price: float = None) -> Tuple[bool, str, List[Trade]]:
        """
        Primary entry point for agents to submit orders.
        """
        current_dt = self._get_current_time()
        current_time = current_dt.time()
        timestamp = current_dt.timestamp()

        # Create order using the pool
        order_id = self._get_next_order_id()
        order = self.order_pool.get_order(
            order_id, agent_id, side, quantity, order_type, 
            timestamp, price, trigger_price
        )

        # 1. Compliance Validation
        is_valid, reason = self.compliance_engine.validate_order(order, current_time)
        if not is_valid:
            self.order_pool.release_order(order)
            return False, reason, []

        # 2. Order Matching
        trades, _ = self.matching_engine.match_order(order)

        # 3. Post-Trade Compliance Checks
        if trades:
            last_trade_price = trades[-1].price
            self.compliance_engine.post_trade_check(last_trade_price, current_time)
        
        # If the original order object was mutated and not fully filled, it now rests
        # in the book. If it was fully filled, its quantity is 0. If it was a market
        # order that was not fully filled and cancelled, its quantity is > 0.
        # We don't release it back to the pool unless it was explicitly cancelled.

        return True, "Order accepted.", trades

    def cancel_order(self, order_id: int) -> bool:
        """
        Allows an agent to cancel a pending order.
        """
        cancelled_order = self.order_book.cancel_order(order_id)
        if cancelled_order:
            self.order_pool.release_order(cancelled_order)
            return True
        return False
