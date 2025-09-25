"""
Implements the core Limit Order Book (LOB) data structure.

The LOB is implemented using SortedDicts for buys (bids) and sells (asks),
which provides logarithmic time complexity for adding new price levels.
Each price level (Limit) contains a doubly-linked list of Orders,
allowing for constant time complexity for cancellations.
"""
from typing import Optional, Dict
from sortedcontainers import SortedDict
from .orders import Order, OrderSide

class Limit:
    """
    Represents a single price level in the order book.

    This class holds all orders at a specific price, forming a queue
    implemented as a doubly-linked list.
    """
    def __init__(self, price: float):
        self.price = price
        self.total_volume: int = 0
        self.order_count: int = 0
        
        # Pointers to the head and tail of the order queue (doubly-linked list)
        self.head_order: Optional[Order] = None
        self.tail_order: Optional[Order] = None

        # Binary tree pointers (conceptual - managed by SortedDict)
        # self.parent = None
        # self.left_child = None
        # self.right_child = None
        
    def add_order(self, order: Order):
        """Adds an order to the end of the queue at this price level."""
        if self.head_order is None:
            self.head_order = order
            self.tail_order = order
        else:
            self.tail_order.next_order = order
            order.prev_order = self.tail_order
            self.tail_order = order
        
        self.total_volume += order.quantity
        self.order_count += 1
        order.parent_limit = self

    def remove_order(self, order: Order):
        """Removes a specific order from the queue."""
        self.total_volume -= order.quantity
        self.order_count -= 1

        if order.prev_order:
            order.prev_order.next_order = order.next_order
        if order.next_order:
            order.next_order.prev_order = order.prev_order

        if self.head_order == order:
            self.head_order = order.next_order
        if self.tail_order == order:
            self.tail_order = order.prev_order
            
        order.parent_limit = None

    def __repr__(self):
        return f"Limit(Price={self.price}, Vol={self.total_volume}, Orders={self.order_count})"

class OrderBook:
    """
    The main OrderBook engine.

    It manages the buy and sell sides of the book, holding price Limits in
    efficient sorted data structures.
    """
    def __init__(self):
        # Bids are stored in descending order of price (best price is highest)
        # We achieve this by negating the price keys.
        self.bids: SortedDict[float, Limit] = SortedDict()
        
        # Asks are stored in ascending order of price (best price is lowest)
        self.asks: SortedDict[float, Limit] = SortedDict()
        
        # Direct access to all active orders for O(1) cancellation
        self._orders: Dict[int, Order] = {}

    def add_order(self, order: Order):
        """
        Adds a new limit order to the book.
        
        Note: Market orders are handled by the MatchingEngine, not added here.
        """
        if order.order_id in self._orders:
            raise ValueError(f"Order with ID {order.order_id} already exists.")

        price = order.price
        if order.side == OrderSide.BUY:
            book_side = self.bids
            # Use negative price for key to sort bids descendingly
            key = -price
        else:
            book_side = self.asks
            key = price

        if key not in book_side:
            book_side[key] = Limit(price)
            
        limit_level = book_side[key]
        limit_level.add_order(order)
        self._orders[order.order_id] = order
        
    def cancel_order(self, order_id: int) -> Optional[Order]:
        """
        Cancels an existing order from the book in O(1) time.
        """
        order = self._orders.pop(order_id, None)
        if not order:
            return None # Order not found

        limit_level = order.parent_limit
        if limit_level:
            limit_level.remove_order(order)
            
            # If the limit level is now empty, remove it from the book
            if limit_level.order_count == 0:
                if order.side == OrderSide.BUY:
                    del self.bids[-limit_level.price]
                else:
                    del self.asks[limit_level.price]
        return order

    @property
    def best_bid(self) -> Optional[float]:
        """Returns the highest bid price, or None if no bids exist."""
        if not self.bids:
            return None
        # The first key in bids SortedDict is the highest bid (due to negative key)
        return self.bids.peekitem(0)[1].price

    @property
    def best_ask(self) -> Optional[float]:
        """Returns the lowest ask price, or None if no asks exist."""
        if not self.asks:
            return None
        # The first key in asks SortedDict is the lowest ask
        return self.asks.peekitem(0)[1].price
        
    def get_order(self, order_id: int) -> Optional[Order]:
        """Retrieves an order by its ID."""
        return self._orders.get(order_id)

    def __repr__(self):
        # Create a visual representation of the order book
        lines = []
        
        # Asks (sorted ascending)
        for _, limit in reversed(self.asks.items()):
            lines.append(f"ASK: {limit.price:.2f} | {limit.total_volume}")
        
        lines.append("-" * 30)

        # Bids (sorted descending)
        for _, limit in self.bids.items():
            lines.append(f"BID: {limit.price:.2f} | {limit.total_volume}")
            
        return "\n".join(lines)
