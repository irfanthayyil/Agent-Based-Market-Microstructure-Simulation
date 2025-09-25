"""
Implements the order matching logic based on strict price-time priority.
"""
from typing import List, Tuple
from .order_book import OrderBook
from .orders import Order, OrderSide, OrderType

class Trade:
    """Represents a single trade execution."""
    def __init__(self, maker_order_id: int, taker_order_id: int, 
                 price: float, quantity: int, timestamp: float):
        self.maker_order_id = maker_order_id
        self.taker_order_id = taker_order_id
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        
    def __repr__(self):
        return (f"Trade(Taker={self.taker_order_id}, Maker={self.maker_order_id}, "
                f"Qty={self.quantity} @ {self.price})")

class MatchingEngine:
    """
    Processes incoming orders and matches them against the order book.
    """
    def __init__(self, order_book: OrderBook):
        self.order_book = order_book
        self._trade_id_counter = 0

    def _generate_trade_id(self) -> int:
        self._trade_id_counter += 1
        return self._trade_id_counter

    def match_order(self, incoming_order: Order) -> Tuple[List[Trade], List[Order]]:
        """
        Matches an incoming order against the book.

        Args:
            incoming_order: The new order to be processed.

        Returns:
            A tuple containing:
            - A list of trades that occurred.
            - A list of orders that were fully or partially filled (makers).
        """
        trades = []
        filled_maker_orders = []
        
        if incoming_order.side == OrderSide.BUY:
            book_to_match = self.order_book.asks
            is_matchable = lambda price: self.order_book.best_ask and price >= self.order_book.best_ask
        else: # SELL
            book_to_match = self.order_book.bids
            is_matchable = lambda price: self.order_book.best_bid and price <= self.order_book.best_bid

        # Handle Market and Limit orders that can be matched immediately
        price_condition = (is_matchable(incoming_order.price) if incoming_order.order_type == OrderType.LIMIT 
                           else bool(book_to_match))
        
        while incoming_order.quantity > 0 and price_condition:
            best_price_limit = book_to_match.peekitem(0)[1]
            
            # Iterate through orders at this price level in time priority
            current_order_node = best_price_limit.head_order
            while current_order_node and incoming_order.quantity > 0:
                trade_quantity = min(incoming_order.quantity, current_order_node.quantity)
                
                # *** BUG FIX STARTS HERE ***
                # Explicitly reduce the total volume at the price level.
                best_price_limit.total_volume -= trade_quantity
                # *** BUG FIX ENDS HERE ***

                trade = Trade(
                    maker_order_id=current_order_node.order_id,
                    taker_order_id=incoming_order.order_id,
                    price=best_price_limit.price,
                    quantity=trade_quantity,
                    timestamp=incoming_order.timestamp
                )
                trades.append(trade)

                incoming_order.quantity -= trade_quantity
                current_order_node.quantity -= trade_quantity
                
                next_order_node = current_order_node.next_order
                
                if current_order_node.quantity == 0:
                    filled_maker_orders.append(current_order_node)
                    # Note: cancel_order also updates volume, but since the order's
                    # quantity is now 0, its effect is neutral. Our manual reduction above
                    # handles the actual traded volume.
                    self.order_book.cancel_order(current_order_node.order_id)
                
                current_order_node = next_order_node

            # Update price condition for the next loop iteration
            price_condition = (is_matchable(incoming_order.price) if incoming_order.order_type == OrderType.LIMIT
                               else bool(book_to_match))

        # If the incoming order has remaining quantity, it's a limit order that
        # rests on the book.
        if incoming_order.quantity > 0 and incoming_order.order_type == OrderType.LIMIT:
            self.order_book.add_order(incoming_order)
            
        return trades, filled_maker_orders

