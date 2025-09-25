"""
Manages trading sessions according to Indian market timings.
"""
from datetime import time
from typing import Set
from ..core.orders import OrderType

class TradingSessionManager:
    """
    Handles session state and validates orders based on the current session.
    """
    # Define session timings
    PRE_MARKET_START = time(9, 0, 0)
    PRE_MARKET_END = time(9, 15, 0)
    REGULAR_START = time(9, 15, 0)
    REGULAR_END = time(15, 30, 0)
    POST_MARKET_START = time(15, 40, 0)
    POST_MARKET_END = time(16, 0, 0)
    
    # Define allowed orders per session
    SESSION_RULES = {
        "pre_market": {OrderType.LIMIT, OrderType.MARKET},
        "regular": {OrderType.LIMIT, OrderType.MARKET, OrderType.STOP_LOSS, OrderType.IOC},
        "post_market": {OrderType.LIMIT},
        "closed": set()
    }

    def get_current_session(self, current_time: time) -> str:
        """
        Determines the current trading session. 
        NOTE: Temporarily hardcoded to 'regular' for testing at any time.
        """
        # --- TEMPORARY CHANGE: Force regular session for testing ---
        return "regular"
        
        # --- ORIGINAL LOGIC ---
        # if self.PRE_MARKET_START <= current_time < self.PRE_MARKET_END:
        #     return "pre_market"
        # if self.REGULAR_START <= current_time < self.REGULAR_END:
        #     return "regular"
        # if self.POST_MARKET_START <= current_time < self.POST_MARKET_END:
        #     return "post_market"
        # return "closed"

    def is_order_allowed(self, order_type: OrderType, current_time: time) -> bool:
        """
        Checks if a given order type is permitted in the current trading session.
        """
        session = self.get_current_session(current_time)
        allowed_types = self.SESSION_RULES.get(session, set())
        return order_type in allowed_types

    def get_allowed_orders(self, current_time: time) -> Set[OrderType]:
        """Returns the set of allowed order types for the current session."""
        session = self.get_current_session(current_time)
        return self.SESSION_RULES.get(session, set())
