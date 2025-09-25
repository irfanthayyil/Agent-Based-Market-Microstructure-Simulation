"""
Defines the market data feed for broadcasting events to agents.
"""
from typing import List
from .agent_interface import Agent

class MarketDataFeed:
    """
    Broadcasts exchange events to all subscribed agents.
    Implements a simple observer pattern.
    """
    def __init__(self):
        self._subscribers: List[Agent] = []

    def subscribe(self, agent: Agent):
        """Add an agent to the subscription list."""
        if agent not in self._subscribers:
            self._subscribers.append(agent)
    
    def unsubscribe(self, agent: Agent):
        """Remove an agent from the subscription list."""
        self._subscribers.remove(agent)

    def broadcast(self, market_data: dict):
        """
        Send market data to all subscribed agents.
        This would be called by the Exchange on events like trades or book updates.
        """
        for agent in self._subscribers:
            try:
                agent.on_market_update(market_data)
            except Exception as e:
                print(f"Error updating agent {agent.agent_id}: {e}")
