import unittest

from src.utils import determine_lost_souls_required


class TestUtils(unittest.TestCase):
    """Tests for utility functions in utils.py."""

    def test_determine_lost_souls_required_valid_ranges(self):
        """Test determine_lost_souls_required for valid deck sizes."""
        test_cases = [
            (50, 7),
            (56, 7),
            (57, 8),
            (63, 8),
            (64, 9),
            (70, 9),
            (71, 10),
            (77, 10),
            (78, 11),
            (84, 11),
            (85, 12),
            (91, 12),
            (92, 13),
            (98, 13),
            (99, 14),
            (105, 14),
        ]

        for deck_size, expected in test_cases:
            with self.subTest(deck_size=deck_size):
                result = determine_lost_souls_required(deck_size)
                self.assertEqual(result, expected, f"Failed for deck size {deck_size}")

    def test_determine_lost_souls_required_invalid_ranges(self):
        """Test determine_lost_souls_required raises ValueError for out of range deck sizes."""
        invalid_deck_sizes = [40]

        for deck_size in invalid_deck_sizes:
            with self.subTest(deck_size=deck_size), self.assertRaises(ValueError):
                determine_lost_souls_required(deck_size)


if __name__ == "__main__":
    unittest.main()
