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
        else:
            self.subtype = None

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

    def search_for(
        self,
        card_type: Optional[str] = None,
        top_n: int = None,
        subtype: Optional[str] = None,
    ) -> Optional[Card]:
        """
        Search for and remove a card of the given type or subtype from the top N cards of the zone.
        At least one of card_type or subtype must be provided.
        If top_n is None, search the entire zone.

        Args:
        card_type (str, optional): The type of card to search for. Defaults to None.
        top_n (int, optional): The number of cards from the start of the zone to search through.
        subtype (str, optional): The subtype of card to search for. Defaults to None.

        Returns:
        Optional[Card]: The found card, or None if not found.
        """
        # Ensure at least one of card_type or subtype is provided
        if not card_type and not subtype:
            raise ValueError("At least one of card_type or subtype must be provided.")

        cards_to_search = (
            list(self.cards)[:top_n] if top_n is not None else list(self.cards)
        )
        for card in cards_to_search:
            if (card_type and card.card_type == card_type) or (
                subtype and hasattr(card, "subtype") and card.subtype == subtype
            ):
                self.cards.remove(card)
                if card_type:
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

    def top_cards(self, cards: deque[Card]) -> None:
        """Add cards to the top of the deck."""
        for card in reversed(cards):
            self.cards.appendleft(card)

    @property
    def cards_in_deck(self):
        """Return the number of cards left in deck"""
        return len(self.cards)

    def resolve_the_virgin_birth(self, virgin_birth_card: Card) -> Card:
        """Look at the top six cards of deck. Grab one, and bottom virgin_birth."""
        top_six_cards = self.draw_n(6)
        # Define the priority of card types
        priority_order = (
            "macguffin",
            "tutor",
            "lost_soul",
        )
        output = None

        for priority in priority_order:
            for card in list(top_six_cards):
                if card.card_type == priority:
                    output = card
                    top_six_cards.remove(card)
                    break
            if output:  # If a card has been selected, exit the outer loop
                break
        if not output:
            output = top_six_cards[0]

        # Put the remaining cards back on top and the virgin_birth_card at the bottom
        self.top_cards(top_six_cards)
        self.bottom_cards(deque([virgin_birth_card]))

        return output
