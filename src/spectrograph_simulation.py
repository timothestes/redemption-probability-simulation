import csv
import os

from src.decklist import Decklist


class SpectrographSimulation:
    """Class contains all information necessary to run a spectrograph simulation."""

    def __init__(self, deck_file_path: str, cycler_logic: str):
        self.deck_file_path = deck_file_path
        self.cycler_logic = cycler_logic

    @staticmethod
    def create_empty_log_file():
        """Used to track information of games played."""
        headers = [
            "deck_size",
        ]

        with open("game_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    def initialize_deck(self):
        """Load the deck in."""
        self.raw_deck = self._load_raw_deck(self.deck_file_path)

    @staticmethod
    def _load_raw_deck(deck_file_path: str) -> Decklist:
        """Read a txt file into a variable."""
        if not deck_file_path:
            raise AssertionError("Please provide a deck_file_path")

        if not os.path.isfile(deck_file_path):
            raise FileNotFoundError(f"No file found at {deck_file_path}")

        if not deck_file_path.endswith(".txt"):
            raise AssertionError("File must be a .txt file")

        return Decklist(deck_file_path)
