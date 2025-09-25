"""
Contains the definitions for Order objects and an object pool for memory efficiency.
"""
from __future__ import annotations
from collections import deque
from enum import Enum
from typing import Optional, TYPE_CHECKING

# This block is only executed during static type checking, not at runtime.
# without causing a circular import error.
if TYPE_CHECKING:
    from .order_book import Limit

class OrderSide(Enum):
    """Enumeration for order side (BUY or SELL)."""
    BUY = 1
    SELL = -1

class OrderType(Enum):
    """Enumeration for different types of orders."""
    MARKET = 1
    LIMIT = 2
    STOP_LOSS = 3
    IOC = 4
    FOK = 5

class Order:
    """
    Represents a single order in the Limit Order Book.

    This object is designed to be part of a doubly-linked list at its price level (Limit),
    allowing for O(1) cancellation.
    """
    def __init__(self, order_id: int, agent_id: int, side: OrderSide, 
                 quantity: int, order_type: OrderType, timestamp: float, 
                 price: Optional[float] = None, trigger_price: Optional[float] = None):
        """
        Initializes an Order object.
        
        Args:
            order_id: Unique identifier for the order.
            agent_id: Identifier for the agent placing the order.
            side: The side of the order (BUY or SELL).
            quantity: The number of shares.
            order_type: The type of the order (MARKET, LIMIT, etc.).
            timestamp: The time the order was placed.
            price: The limit price for LIMIT orders.
            trigger_price: The price for activating a STOP_LOSS order.
        """
        self.order_id = order_id
        self.agent_id = agent_id
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.timestamp = timestamp
        self.price = price
        self.trigger_price = trigger_price

        # Pointers for the doubly-linked list at a Limit (price) level
        self.next_order: Optional[Order] = None
        self.prev_order: Optional[Order] = None
        
        # Reference to the parent Limit object
        self.parent_limit: Optional[Limit] = None

    def __repr__(self):
        return (f"Order(ID={self.order_id}, Side={self.side.name}, Qty={self.quantity}, "
                f"Price={self.price}, Type={self.order_type.name})")

class OrderPool:
    """
    An object pool for recycling Order objects to reduce garbage collection overhead.
    This is crucial for high-performance simulations where millions of orders can be
    created and destroyed.
    """
    def __init__(self, initial_size: int = 100000):
        """Initializes the pool with a predefined number of Order objects."""
        self._pool = deque()
        self._expand_pool(initial_size)

    def _expand_pool(self, size: int):
        """Creates new Order objects and adds them to the pool."""
        for _ in range(size):
            # Initialize with dummy values
            self._pool.append(Order(0, 0, OrderSide.BUY, 0, OrderType.LIMIT, 0.0))

    def get_order(self, *args, **kwargs) -> Order:
        """
        Retrieves an order from the pool and re-initializes it with new parameters.
        If the pool is empty, it expands it.
        """
        if not self._pool:
            self._expand_pool(len(self._pool) // 2 or 1000) # Expand by 50% or 1000
        
        order = self._pool.popleft()
        # Re-initialize the recycled order object
        order.__init__(*args, **kwargs)
        return order

    def release_order(self, order: Order):
        """
        Resets an Order object and returns it to the pool for future use.
        """
        # Reset pointers and parent references to prevent memory leaks
        order.next_order = None
        order.prev_order = None
        order.parent_limit = None
        self._pool.append(order)

