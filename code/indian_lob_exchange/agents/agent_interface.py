"""
Defines the base interface for trading agents.
Researchers will subclass this to create their custom agent logic.
"""
from abc import ABC, abstractmethod

class Agent(ABC):
    """
    Abstract Base Class for all trading agents.
    """
    def __init__(self, agent_id: int, exchange):
        self.agent_id = agent_id
        self.exchange = exchange # Agents need a reference to the exchange

    @abstractmethod
    def on_market_update(self, market_data):
        """
        Callback for when market data (e.g., new trade, book change) is available.
        """
        pass

    @abstractmethod
    def place_order(self):
        """
        Agent's logic for placing an order goes here.
        """
        pass

    def get_portfolio(self):
        """
        Placeholder for portfolio management.
        """
        print(f"Agent {self.agent_id} portfolio not implemented.")
