"""
Implements SEBI-compliant circuit breaker and price band logic.
"""
from datetime import time

class CircuitBreakerMonitor:
    """
    Monitors market prices against index-level and stock-level circuit breakers.
    """
    INDEX_CIRCUIT_BREAKERS = {
        0.10: {"before_1pm": 45, "1pm_to_230pm": 15, "after_230pm": 0},
        0.15: {"before_1pm": 105, "1pm_to_230pm": 45, "after_230pm": "close_market"},
        0.20: "halt_for_day"
    }

    STOCK_PRICE_BANDS = {
        "category_1": 0.02,
        "category_2": 0.05,
        "category_3": 0.10,
        "fno_stocks": {"band": 0.10, "cooling_period": 15},
        "default": 0.20
    }

    def __init__(self, reference_price: float, stock_category: str = "default"):
        self.reference_price = reference_price
        self.stock_category = stock_category
        self.market_halted = False
        self.halt_end_time = None
        
        self._price_band = self._get_price_band()
        self.upper_band = self.reference_price * (1 + self._price_band)
        self.lower_band = self.reference_price * (1 - self._price_band)

    def _get_price_band(self) -> float:
        """Determines the price band percentage for the stock."""
        band_info = self.STOCK_PRICE_BANDS.get(self.stock_category, self.STOCK_PRICE_BANDS["default"])
        return band_info["band"] if isinstance(band_info, dict) else band_info
        
    def check_price_band(self, order_price: float) -> bool:
        """
        Validates if an order's price is within the daily price band.
        Returns True if valid, False otherwise.
        """
        if self.lower_band <= order_price <= self.upper_band:
            return True
        return False

    def check_index_circuit_breaker(self, current_price: float, current_time: time) -> dict:
        """
        Checks if the current price triggers an index-level circuit breaker.
        
        Returns a dictionary with halt information if triggered.
        """
        price_change = abs(current_price - self.reference_price) / self.reference_price
        
        triggered_level = 0
        if price_change >= 0.20:
            triggered_level = 0.20
        elif price_change >= 0.15:
            triggered_level = 0.15
        elif price_change >= 0.10:
            triggered_level = 0.10
            
        if not triggered_level:
            return {"triggered": False}

        halt_info = self.INDEX_CIRCUIT_BREAKERS[triggered_level]

        if isinstance(halt_info, str): # 20% case
            return {"triggered": True, "action": halt_info}

        # 10% or 15% case, depends on time
        if current_time < time(13, 0):
            action = halt_info["before_1pm"]
        elif time(13, 0) <= current_time < time(14, 30):
            action = halt_info["1pm_to_230pm"]
        else:
            action = halt_info["after_230pm"]
            
        return {"triggered": True, "level": triggered_level, "action": action}
