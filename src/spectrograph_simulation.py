import csv
import os
import random

from src.constants import CYCLER_SOULS, DARKNESS, EVIL_BRIGADES, GOOD_BRIGADES, LAWLESS
from src.decklist import Decklist
from src.models_v2 import Deck, Discard, Hand, Territory

MATTHEW_CSV_FILE = "matthew_game_log.csv"


class SpectrographSimulation:
    """Class contains all information necessary to run a spectrograph simulation."""

    def __init__(
        self,
        deck_file_path: str,
        n_simulations: int,
        cycler_logic: str,
        crowds_ineffectiveness_weight: float,
        matthew_fizzle_rate: float,
    ):
        self.deck_file_path = deck_file_path
        self.n_simulations = n_simulations
        self.cycler_logic = cycler_logic
        self.crowds_ineffectiveness_weight = crowds_ineffectiveness_weight
        self.matthew_fizzle_rate = matthew_fizzle_rate

    @staticmethod
    def create_empty_log_file():
        """Used to track information of games played."""
        headers = [
            "sim_number",
            "n_cards_matthew_drew",
            "deck_size",
        ]

        with open(MATTHEW_CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    def initialize_decklist(self):
        """Load the deck in."""
        self.decklist = self._load_raw_deck(self.deck_file_path)
        self.deck = Deck.load_decklist(self.decklist)
        self.territory = Territory(cards=[])
        self.discard = Discard(cards=[])
        self.hand = Hand(cards=[])
        # this makes it so that the simulation keeps 8 cards in hand.
        self._set_flags(self.decklist)

    def _set_flags(self, decklist: Decklist):
        """Set some flags that might be useful later."""
        self.going_first = True
        self.virgin_birth = False
        self.crowds = False
        for card in decklist.mapped_main_deck_list:
            if card == "Virgin Birth":
                self.virgin_birth = True
            if card == 'Lost Soul "Crowds" [Luke 5:15] [2016 - Local]':
                self.crowds = True

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

    def _reset_simulation_state(self):
        """Reset the state of the simulation for a new run."""
        self.deck.reset(shuffle=True)
        self.territory.reset()
        self.discard.reset()
        self.hand.reset()

    def _draw_cards(self, n_cards: int, resolve_stars=False):
        """Handle anytime we draw cards during the game."""
        drawn_cards = self.deck.draw_n(n_cards)

        if resolve_stars:
            # resolve the virgin birth
            if self.virgin_birth:
                for i, card in enumerate(drawn_cards):
                    if card.name == "Virgin Birth":
                        # replace virgin birth with a card from the top 6
                        drawn_cards[i] = self.deck.resolve_the_virgin_birth(
                            drawn_cards[i]
                        )

        self.hand.add(drawn_cards)

        # handle lost souls that are in our hand
        while self.hand.count(type="Lost Soul") > 0:
            # put any lost souls in play
            lost_soul = self.hand.remove(type="Lost Soul")
            self.territory.add(lost_soul)
            # don't draw from empty deck
            if not self.deck.cards_in_deck == 0:
                # then redraw
                self.hand.add(self.deck.draw_n(1))

            if lost_soul.name in CYCLER_SOULS:
                self._resolve_cycler()
            elif lost_soul.name == 'Lost Soul "Prosperity" [Deuteronomy 30:15]':
                self._resolve_prosperity()
            elif lost_soul.name in DARKNESS:
                self._resolve_darkness()
            elif lost_soul.name in LAWLESS:
                self._resolve_lawless()

    def _resolve_darkness(self):
        """Randomly choose an evil character from deck and add it to hand"""
        # TODO: Logic currently cannot get dual-alignment evil characters
        evil_character = self.deck.search_for(type="Evil Character")
        if evil_character:
            self.hand.add(evil_character)

    def _resolve_prosperity(self):
        """Discard a card and draw 2 cards."""
        self.discard.add(self.hand.remove(type="RandomNonLostSoul"))
        self.hand.add(self.deck.draw_n(2))

    def _resolve_cycler(self):
        """Underdeck a random card and draw a card."""
        self.deck.bottom_cards([self.hand.remove(type="RandomNonLostSoul")])
        self.hand.add(self.deck.draw_n(1))

    def _resolve_lawless(self):
        """Reveal top 6, put lost souls in play, and grab an evil card."""
        top_six = self.deck.draw_n(6)
        got_evil = False
        for i, card in enumerate(top_six):
            if card.type == "Lost Soul":
                self.territory.add(top_six.pop(i))
                if card.name in CYCLER_SOULS:
                    self._resolve_cycler()
            elif not got_evil and card.alignment == "Evil":
                # TODO: Logic can't currently grab three woes or other "evil" neutral cards...
                self.hand.add(top_six.pop(i))
                got_evil = True
        # underdeck the rest
        self.deck.bottom_cards(top_six)

    def _watch_matthew_take_a_turn(self, sim_number) -> dict:
        """Actions to take when when Matthew inevitably attacks."""
        if random.random() < self.matthew_fizzle_rate:
            # matthew deck fizzled
            n_brigades_in_hand = 0
        # crowds lost soul logic
        elif (
            self.crowds
            # if we drew crowds
            and self.territory.count(
                name='Lost Soul "Crowds" [Luke 5:15] [2016 - Local]'
            )
            > 0
            # factor in the times matthew decks will have an answer
            and random.random() > self.crowds_ineffectiveness_weight
        ):
            # we have hand protection. 0 brigades drawn with Matthew
            n_brigades_in_hand = 0
        else:
            n_brigades_in_hand = self._count_n_brigades_in_hand()
        return {
            "sim_number": sim_number,
            "n_cards_matthew_draw": n_brigades_in_hand,
            "deck_size": self.decklist.deck_size,
        }

    def _count_n_brigades_in_hand(self) -> int:
        """
        Count the number of unique brigades in hand, handling 'multi' brigade specially.
        """
        brigades = set()
        for card in self.hand.cards:
            brigades.update(card.brigade)

        expanded_brigades = set()
        for brigade in brigades:
            if brigade == "Good Multi":
                expanded_brigades.update(GOOD_BRIGADES)
            elif brigade == "Evil Multi":
                expanded_brigades.update(EVIL_BRIGADES)
            else:
                expanded_brigades.add(brigade)

        return len(expanded_brigades)

    @staticmethod
    def append_log_to_file(log_data: list[dict], csv_file: str):
        """Bulk add rows of log data to the CSV file."""
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
            writer.writerows(log_data)

    def run(self):
        """Simulate N games of Redemption by drawing 8 cards from a deck."""
        all_logs = []  # Collect all logs to write in bulk
        for sim_number in range(self.n_simulations):
            self._reset_simulation_state()  # Reset deck, hand, discard, and territory

            # draw 8 cards from deck
            self._draw_cards(n_cards=8, resolve_stars=True)

            # watch matthew take a turn
            turn_log = self._watch_matthew_take_a_turn(sim_number)

            # Collect logs
            all_logs.append(turn_log)

        # # Bulk write logs at the end of all simulations
        self.append_log_to_file(all_logs, MATTHEW_CSV_FILE)

    def print_results(self):
        """Print the summary statistics of the simulation."""
        column_sum = 0
        total_rows = 0

        # Calculate average of the 'n_cards_matthew_drew' column
        with open(MATTHEW_CSV_FILE, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                try:
                    column_sum += float(row["n_cards_matthew_drew"])
                    total_rows += 1
                except (ValueError, KeyError):
                    continue  # Handle non-numeric values or missing keys

        if total_rows > 0:
            average_second_column = column_sum / total_rows
            print(f"Average number of cards Matthew drew: {average_second_column}")
        else:
            print("No valid data found")
