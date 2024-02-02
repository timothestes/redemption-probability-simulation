"""
Defines the data models used in the Redemption Probability Simulation project.

This module contains class definitions for Cards, Zones (and its specialized forms like Hand, 
Territory, and Discard Pile), and the Deck. These models are essential for representing the state 
and behavior of various components within a card game simulation.
"""

import random
from collections import deque
from typing import Optional

CARD_TYPES = ["lost_soul", "non_lost_soul", "macguffin", "tutor"]


class Card:
    def __init__(self, card_type: str, subtype: Optional[str] = None):
        self.card_type = card_type
        if subtype:
            self.subtype = subtype

    def __str__(self):
        return f"{self.card_type} card"


class Zone:
    def __init__(self, cards: Optional[deque[Card]] = None):
        self.cards = cards or deque()
        self._card_types = {card_type: 0 for card_type in CARD_TYPES}
        for card in self.cards:
            self._card_types[card.card_type] += 1

    def add(self, cards):
        """Add a list or single card to a given zone."""
        if isinstance(cards, list) or isinstance(cards, deque):
            for card in cards:
                self.append(card)
        else:
            self.append(cards)

    def append(self, card: Card):
        """Add a single card to a given zone."""
        self.cards.append(card)
        self._card_types[card.card_type] += 1

    def count(self, card_type: str):
        """Get the count of the number of cards of a given type in the zone."""
        return self._card_types.get(card_type, 0)

    def remove(self, card_type: str = None):
        """Remove and return a card of the given type from the zone."""
        if not card_type:
            removed_card = self.cards.popleft()
            self._card_types[removed_card.card_type] -= 1
            return removed_card

        for card in list(self.cards):  # Convert deque to list for iteration
            if card.card_type == card_type:
                self.cards.remove(card)
                self._card_types[card.card_type] -= 1
                return card
        return None

    def search_for(self, card_type: str) -> Optional[Card]:
        """Search for and remove a card of the given type from the zone, if found."""
        for card in list(self.cards):  # Convert deque to list for iteration
            if card.card_type == card_type:
                self.cards.remove(card)
                self._card_types[card.card_type] -= 1
                return card
        return None

    def shuffle(self):
        """Randomize the order of cards."""
        self.cards = deque(random.sample(self.cards, len(self.cards)))


class Hand(Zone):
    """Zone used to represent the Hand."""

    def __init__(self, cards: Optional[deque[Card]] = None):
        super().__init__(cards if cards else deque())


class Territory(Zone):
    """Zone used to represent the Territory."""

    def __init__(self, cards: Optional[deque[Card]] = None):
        super().__init__(cards if cards else deque())


class Discard(Zone):
    """Zone used to represent the Discard Pile."""

    def __init__(self, cards: Optional[deque[Card]] = None):
        super().__init__(cards if cards else deque())


class Deck(Zone):
    """Zone used to represent the deck."""

    def __init__(self, cards: Optional[deque[Card]] = None):
        super().__init__(cards if cards else deque())

    def draw_n(self, number_of_cards_to_draw: int) -> deque[Card]:
        """Return the first n cards of the deck."""
        if number_of_cards_to_draw <= 0:
            raise ValueError("Number of cards to draw should be greater than zero.")

        drawn_cards = deque()
        for _ in range(min(number_of_cards_to_draw, len(self.cards))):
            drawn_cards.append(self.cards.popleft())
        return drawn_cards

    def bottom_cards(self, cards: deque[Card], random_order=False) -> None:
        """Return some cards to the bottom of the deck."""
        if random_order:
            cards = deque(random.sample(cards, len(cards)))
        self.cards.extend(cards)

    @property
    def cards_in_deck(self):
        """Return the number of cards left in deck"""
        return len(self.cards)
