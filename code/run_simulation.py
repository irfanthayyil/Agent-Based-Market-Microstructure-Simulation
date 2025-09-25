"""
An example script demonstrating how to use the Indian LOB Exchange.
This sets up the exchange and simulates a few basic order submissions.
"""
from indian_lob_exchange.exchange import Exchange
from indian_lob_exchange.core.orders import OrderSide, OrderType

def main():
    """Main simulation function."""
    print("--- Initializing Indian LOB Exchange Simulation ---")
    
    # Initialize the exchange with a reference price of 100.0 for compliance checks
    exchange = Exchange(reference_price=100.0, stock_category="fno_stocks")
    
    print("\n--- Current Order Book (Empty) ---")
    print(exchange.order_book)
    print("-" * 35)

    # --- SCENARIO 1: Building the book ---
    print("\n--- Scenario 1: Agents submit limit orders to build the book ---")
    exchange.submit_order(agent_id=1, side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT, price=99.0)
    exchange.submit_order(agent_id=2, side=OrderSide.BUY, quantity=5, order_type=OrderType.LIMIT, price=98.0)
    exchange.submit_order(agent_id=3, side=OrderSide.SELL, quantity=8, order_type=OrderType.LIMIT, price=101.0)
    exchange.submit_order(agent_id=4, side=OrderSide.SELL, quantity=12, order_type=OrderType.LIMIT, price=102.0)
    
    print("\n--- Current Order Book ---")
    print(exchange.order_book)
    print(f"Best Bid: {exchange.order_book.best_bid}, Best Ask: {exchange.order_book.best_ask}")
    print("-" * 35)
    
    # --- SCENARIO 2: A market order crosses the spread ---
    print("\n--- Scenario 2: A buyer submits a market order for 10 shares ---")
    # This should match against the 8 shares at 101.0 first, then 2 shares at 102.0
    accepted, reason, trades = exchange.submit_order(agent_id=5, side=OrderSide.BUY, quantity=10, order_type=OrderType.MARKET)
    
    print(f"Order Accepted: {accepted}, Reason: {reason}")
    print("Trades Executed:")
    for trade in trades:
        print(f"  - {trade}")
        
    print("\n--- Order Book After Market Order ---")
    print(exchange.order_book)
    print(f"Best Bid: {exchange.order_book.best_bid}, Best Ask: {exchange.order_book.best_ask}")
    print("-" * 35)
    
    # --- SCENARIO 3: Order Cancellation ---
    print("\n--- Scenario 3: Agent 2 cancels their buy order (ID: 2) ---")
    cancelled = exchange.cancel_order(2)
    print(f"Order ID 2 Cancelled Successfully: {cancelled}")

    print("\n--- Order Book After Cancellation ---")
    print(exchange.order_book)
    print(f"Best Bid: {exchange.order_book.best_bid}, Best Ask: {exchange.order_book.best_ask}")
    print("-" * 35)
    
    # --- SCENARIO 4: Price Band Violation Check ---
    print("\n--- Scenario 4: An agent tries to place an order outside the 10% F&O price band ---")
    # Reference price is 100, F&O band is 10%. Upper band is 110.
    accepted, reason, trades = exchange.submit_order(agent_id=6, side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT, price=111.0)
    print(f"Order Accepted: {accepted}, Reason: {reason}")
    print("-" * 35)


if __name__ == "__main__":
    main()
