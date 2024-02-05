import unittest
from collections import deque

from src.models import Card, Deck, Zone


class TestCard(unittest.TestCase):
    """Tests for the Card class."""

    def test_card_initialization(self):
        """Ensure cards are initialized with the correct type."""
        card = Card("macguffin")
        self.assertEqual(card.card_type, "macguffin")

    def test_subtypecard_initialization(self):
        """Ensure cards are initialized with the correct type and optional subtype."""
        card_with_subtype = Card("non_lost_soul", subtype="virgin_birth")
        self.assertEqual(card_with_subtype.subtype, "virgin_birth")


class TestZone(unittest.TestCase):
    """Extended tests for the Zone class with search_for modifications."""

    def setUp(self):
        """Set up a zone with a predefined set of cards for each test."""
        self.cards = deque(
            [
                Card("lost_soul"),
                Card("non_lost_soul"),
                Card("macguffin"),
                Card("tutor"),
                Card("non_lost_soul", subtype="virgin_birth"),
            ]
        )
        self.zone = Zone(self.cards)

    def test_search_for_card_within_n(self):
        """Test searching for and removing a card of a specific type within the first N cards of the zone."""
        card = self.zone.search_for("lost_soul", 2)
        self.assertEqual(card.card_type, "lost_soul")
        # Verify the card is removed from the zone
        self.assertNotIn(card, self.zone.cards)

    def test_search_for_card_beyond_n(self):
        """Test that searching beyond the specified N does not find a card when it's outside the range."""
        card = self.zone.search_for("tutor", 2)
        self.assertIsNone(card)

    def test_search_for_card_without_n(self):
        """Test searching for and removing a card of a specific type without specifying N, should search the entire zone."""
        card = self.zone.search_for("tutor")
        self.assertEqual(card.card_type, "tutor")
        self.assertNotIn(card, self.zone.cards)

    def test_search_for_by_subtype(self):
        """Test searching for and removing a card by subtype."""
        card = self.zone.search_for(subtype="virgin_birth")
        self.assertIsNotNone(card, "Should find a card by its subtype")
        self.assertEqual(
            card.subtype, "virgin_birth", "Found card should have the correct subtype"
        )

    def test_search_for_requires_at_least_one_parameter(self):
        """Test that search_for raises an error if neither card_type nor subtype is provided."""
        with self.assertRaises(ValueError):
            self.zone.search_for()


class TestDeck(unittest.TestCase):
    """Tests for the Deck class."""

    def setUp(self):
        """Set up a deck with a predefined set of cards for each test."""

        self.deck = Deck(
            deque(
                [
                    Card("macguffin"),
                    Card("tutor"),
                    Card("lost_soul"),
                    Card("non_lost_soul"),
                ]
            )
        )

    def test_draw_card(self):
        """Test drawing one card from a deck."""
        card = self.deck.draw_n(1)
        self.assertEqual(len(card), 1)
        self.assertEqual(self.deck.cards_in_deck, 3)

    def test_draw_multiple_cards(self):
        """Test drawing multiple cards from a deck."""
        cards = self.deck.draw_n(2)
        self.assertEqual(len(cards), 2)
        self.assertEqual(self.deck.cards_in_deck, 2)

    def test_bottom_cards(self):
        """Test adding cards to the bottom of a deck."""
        new_cards = deque([Card("tutor"), Card("non_lost_soul")])
        self.deck.bottom_cards(new_cards)
        self.assertEqual(self.deck.cards[-1].card_type, "non_lost_soul")
        self.assertEqual(self.deck.cards[-2].card_type, "tutor")


class TestResolveTheVirginBirth(unittest.TestCase):
    """Test suite for The Virgin Birth."""

    def setUp(self):
        """Set up a deck with a specific composition for each test."""
        self.virgin_birth_card = Card("virgin_birth")
        # Initialize the deck with a known sequence of cards
        self.cards = deque(
            [
                Card("non_lost_soul"),
                Card("tutor"),  # Lower priority card
                Card("macguffin"),  # Higher priority card
                Card("tutor"),  # Another lower priority card for testing
                Card("non_lost_soul"),
                Card("non_lost_soul"),
                Card("non_lost_soul"),
            ]
        )
        self.deck = Deck(self.cards)

    def test_selects_macguffin_over_tutor(self):
        """Ensure a macguffin card is selected over a tutor when present."""
        selected_card = self.deck.resolve_the_virgin_birth(self.virgin_birth_card)
        self.assertEqual(
            selected_card.card_type,
            "macguffin",
            "Macguffin should be selected over tutor",
        )

    def test_selects_tutor_if_no_macguffin(self):
        """Ensure a tutor card is selected if no macguffin card is present."""
        # Manually adjust the deck to remove macguffin cards
        self.cards = deque(
            [card for card in self.cards if card.card_type != "macguffin"]
        )
        self.deck = Deck(self.cards)
        selected_card = self.deck.resolve_the_virgin_birth(self.virgin_birth_card)
        self.assertEqual(
            selected_card.card_type,
            "tutor",
            "Tutor should be selected in the absence of a macguffin",
        )

    def test_virgin_birth_card_bottomed(self):
        """Verify the virgin birth card is placed at the bottom of the deck."""
        self.deck.resolve_the_virgin_birth(self.virgin_birth_card)
        bottom_card = self.deck.cards[-1]
        self.assertEqual(
            bottom_card.card_type,
            "virgin_birth",
            "Virgin birth card should be at the bottom of the deck",
        )

    def test_selection_if_no_priority_cards(self):
        """Verify functionality if no priority cards are present."""
        # Manually adjust the deck to contain only non_lost_soul cards
        self.cards = deque([Card("non_lost_soul") for _ in range(6)])
        self.deck = Deck(self.cards)
        selected_card = self.deck.resolve_the_virgin_birth(self.virgin_birth_card)
        self.assertEqual(type(selected_card), Card)

    def test_functionality_with_less_than_six_cards(self):
        """Test the method's functionality when the deck contains fewer than six cards."""
        # Create a new deck with only 5 cards, including one priority card
        self.cards = deque(
            [
                Card("non_lost_soul"),
                Card("tutor"),  # This should be selected
                Card("non_lost_soul"),
                Card("non_lost_soul"),
                Card("non_lost_soul"),
            ]
        )
        self.deck = Deck(self.cards)

        selected_card = self.deck.resolve_the_virgin_birth(self.virgin_birth_card)
        # Check that the method selects the priority card even in a small deck
        self.assertEqual(
            selected_card.card_type,
            "tutor",
            "Tutor card should be selected in a deck with less than six cards",
        )

        # Also verify the virgin_birth_card is placed at the bottom of the deck
        bottom_card = self.deck.cards[-1]
        self.assertEqual(
            bottom_card.card_type,
            "virgin_birth",
            "Virgin birth card should be placed at the bottom of the deck",
        )

        # Lastly, ensure the total deck size is correct after the operation
        expected_deck_size = 5  # Original 5 minus 1 selected plus 1 virgin_birth_card
        self.assertEqual(
            len(self.deck.cards),
            expected_deck_size,
            "Deck size should be correct after resolving the virgin birth",
        )


if __name__ == "__main__":
    unittest.main()
