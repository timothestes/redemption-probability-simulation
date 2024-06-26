"""
A better version of the models.py module.

This module contains class definitions for Cards, Zones (and its specialized forms like Hand, 
Territory, and Discard Pile), and the Deck. These models are essential for representing the state 
and behavior of various components within a card game simulation.
"""

import random
from typing import List, Optional

from src.decklist import Decklist


class Card:
    def __init__(self, name: str, type: str, brigade: str, alignment: str, **kwargs):
        self.name = name
        self.type = type
        self.brigade = brigade
        self.alignment = alignment
        self.brigades_list = self.brigade.split("/") if self.brigade else []
        # self.__dict__.update(kwargs)  # Update instance with any additional kwargs

    def __str__(self):
        return f"{self.name}"


class Zone:
    def __init__(self, cards: Optional[List[Card]] = None):
        # Store the original state
        self.original_cards = cards.copy() if cards else None
        self.cards = cards or []

    def reset(self):
        """Reset the zone to its original state, if an original state was provided."""
        if self.original_cards is not None:
            self.cards = self.original_cards.copy()
        else:
            self.cards.clear()

    def add(self, cards):
        """Add card(s) to a given zone."""
        if isinstance(cards, list):
            self.cards.extend(cards)
        else:
            self.cards.append(cards)

    def count(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ):
        """Count cards by type and optionally by subtype."""
        # Ensure at least one of name or type is provided
        if not name and not type:
            raise ValueError("At least one of name or type must be provided.")

        return sum(
            1
            for card in self.cards
            if (not name or card.name == name) and (not type or card.type == type)
        )

    def remove(self, name: Optional[str] = None, type: Optional[str] = None):
        """Remove a card by name or type."""
        if not name and not type:
            raise ValueError("At least one of name or type must be provided.")

        for card in self.cards:
            if (not name or card.type == name) and (not type or card.type == type):
                self.cards.remove(card)
                return card
        return None

    def search_for(
        self,
        name: Optional[str] = None,
        type: Optional[str] = None,
        top_n: int = None,
    ) -> Optional[Card]:
        """
        Search for and remove a card of the given name or type from the top N cards of the zone.
        At least one of name or type must be provided.
        If top_n is None, search the entire zone.

        Args:
        name (str, optional): The name of card to search for. Defaults to None.
        type (str, optional): The type of card to search for. Defaults to None.
        top_n (int, optional): The number of cards from the start of the zone to search through.

        Returns:
        Optional[Card]: The found card, or None if not found.
        """
        # Ensure at least one of name or type is provided
        if not name and not type:
            raise ValueError("At least one of name or type must be provided.")

        cards_to_search = (
            self.cards if top_n is None else list(list(self.cards)[:top_n])
        )
        for card in cards_to_search:
            if (name and card.name == name) or (type and card.type == type):
                self.cards.remove(card)
                return card
        return None

    def shuffle(self):
        """Randomize the order of cards."""
        self.cards = list(random.sample(self.cards, len(self.cards)))


class Hand(Zone):
    """Zone used to represent the Hand."""

    def __init__(self, cards: Optional[List[Card]] = None):
        super().__init__(cards if cards else [])


class Territory(Zone):
    """Zone used to represent the Territory."""

    def __init__(self, cards: Optional[List[Card]] = None):
        super().__init__(cards if cards else [])


class Discard(Zone):
    """Zone used to represent the Discard Pile."""

    def __init__(self, cards: Optional[List[Card]] = None):
        super().__init__(cards if cards else [])


class Deck(Zone):
    """Zone used to represent the deck."""

    def __init__(self, cards: Optional[List[Card]] = None):
        super().__init__(cards if cards else [])

    @staticmethod
    def load_decklist(decklist: Decklist) -> "Deck":
        cards = []
        for card_metadata in decklist.mapped_main_deck_list.values():
            for i in range(int(card_metadata["quantity"])):
                cards.append(Card(**card_metadata))
        return Deck(cards)

    def reset(self, shuffle=True):
        """Extend the base reset to optionally shuffle the deck."""
        super().reset()
        if shuffle:
            self.shuffle()

    def draw_n(self, number_of_cards_to_draw: int) -> List[Card]:
        """Return the first n cards of the deck."""
        if number_of_cards_to_draw <= 0:
            raise ValueError("Number of cards to draw should be greater than zero.")

        drawn_cards = []
        for _ in range(min(number_of_cards_to_draw, len(self.cards))):
            drawn_cards.append(self.cards.pop(0))
        return drawn_cards

    def bottom_cards(self, cards: List[Card], random_order=False) -> None:
        """Return some card(s) to the bottom of the deck."""
        if random_order:
            cards = list(random.sample(cards, len(cards)))
        if isinstance(cards, list):
            self.cards.extend(cards)
        else:
            # assuming its just one card
            self.cards.append(cards)

    def top_cards(self, cards: List[Card]) -> None:
        """Add card(s) to the top of the deck."""
        if isinstance(cards, list):
            for card in reversed(cards):
                self.cards.insert(0, card)
        else:
            # assuming its just one card
            self.cards.insert(0, cards)

    @property
    def cards_in_deck(self):
        """Return the number of cards left in deck"""
        return len(self.cards)

    def resolve_the_virgin_birth(self, virgin_birth_card: Card) -> Card:
        """Look at the top six cards of deck. Grab one, and bottom virgin_birth."""
        top_six_cards = self.draw_n(6)
        # TODO: update this logic to not just get the first card
        card_gotten_with_virgin_birth = top_six_cards.pop(0)

        # Put the remaining cards back on top and the virgin_birth_card at the bottom
        self.top_cards(top_six_cards)
        self.bottom_cards(virgin_birth_card)

        return card_gotten_with_virgin_birth
