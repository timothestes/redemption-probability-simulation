import unittest
from collections import deque

from src.models import Card, Deck, Zone


class TestCard(unittest.TestCase):
    """Tests for the Card class."""

    def test_card_initialization(self):
        """Ensure cards are initialized with the correct type."""
        card = Card("macguffin")
        self.assertEqual(card.card_type, "macguffin")


class TestZone(unittest.TestCase):
    """Tests for the Zone class."""

    def setUp(self):
        """Set up a zone with a predefined set of cards for each test."""
        self.cards = deque(
            [Card("lost_soul"), Card("non_lost_soul"), Card("macguffin")]
        )
        self.zone = Zone(self.cards)

    def test_add_single_card(self):
        """Test adding a single card to the zone."""
        new_card = Card("tutor")
        self.zone.add(new_card)
        self.assertIn(new_card, self.zone.cards)

    def test_remove_card(self):
        """Test removing a specific card type from the zone."""
        removed_card = self.zone.remove("macguffin")
        self.assertEqual(removed_card.card_type, "macguffin")
        self.assertNotIn(removed_card, self.zone.cards)

    def test_count_card_type(self):
        """Test counting the number of cards of a specific type in the zone."""
        count = self.zone.count("lost_soul")
        self.assertEqual(count, 1)

    def test_search_for_card(self):
        """Test searching for and removing a card of a specific type from the zone."""
        card = self.zone.search_for("non_lost_soul")
        self.assertEqual(card.card_type, "non_lost_soul")
        self.assertNotIn(card, self.zone.cards)


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


if __name__ == "__main__":
    unittest.main()
