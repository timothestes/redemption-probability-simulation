"""
Contains the core logic for running simulations of the card game Redemption.

This module includes the Simulation class, which encapsulates the logic for simulating games
based on different configurations (e.g., deck sizes, inclusion of specific cards).
It utilizes models defined in models.py and interacts with utility functions and data handling
mechanisms to perform simulations and analyze outcomes.
"""

import csv
import os
from collections import deque

from src.models import Card, Deck, Discard, Hand, Territory
from src.utils import determine_lost_souls_required


class Simulation:
    """Class contains all information necessary to run a simulation."""

    def __init__(
        self,
        macguffin: str,
        deck_size: int,
        n_cycler_souls: list,
        n_tutors: int,
        n_simulations: int,
        n_turns: int,
        going_first: bool,
        hopper: bool,
        virgin_birth: bool,
    ):
        self.macguffin = macguffin
        self.deck_size = deck_size
        self.n_cycler_souls = n_cycler_souls
        self.n_tutors = n_tutors
        self.n_simulations = n_simulations
        self.n_turns = n_turns
        self.going_first = going_first
        self.hopper = hopper
        self.virgin_birth = virgin_birth
        self.souls_in_deck = determine_lost_souls_required(deck_size)
        self.initial_decklist = self.generate_decklist()
        self.deck = Deck(deque(self.initial_decklist))
        self.territory = Territory(cards=[])
        self.discard = Discard(cards=[])
        self.hand = Hand(cards=[])

    def generate_decklist(self) -> deque[Card]:
        """Generate a deck based on certain parameters."""
        deck_of_cards = deque()

        # Initialize deck with specified cards
        deck_of_cards.append(Card("macguffin"))
        deck_of_cards.extend([Card("tutor") for _ in range(self.n_tutors)])
        deck_of_cards.extend(
            [Card("lost_soul", subtype="cycler") for _ in range(self.n_cycler_souls)]
        )
        deck_of_cards.extend(
            [
                Card("lost_soul", subtype="meek")
                for _ in range(self.souls_in_deck - self.n_cycler_souls)
            ]
        )
        if self.hopper:
            deck_of_cards.append(Card("lost_soul", subtype="hopper"))
        if self.virgin_birth:
            deck_of_cards.append(Card("non_lost_soul", subtype="virgin_birth"))
        n_non_lost_souls = self.deck_size - len(deck_of_cards)
        deck_of_cards.extend([Card("non_lost_soul") for _ in range(n_non_lost_souls)])

        return deck_of_cards

    def reset_simulation_state(self):
        """Reset the state of the simulation for a new run."""
        self.deck.reset(shuffle=True)
        self.territory.reset()
        self.discard.reset()
        self.hand.reset()

    def _take_a_turn(
        self,
        turn_number: int,
        sim_number: int,
    ) -> dict:
        """Take a turn of redemption."""
        # draw 3 cards for turn (except if on the play)
        if not (self.going_first and turn_number == 1):
            drawn_cards = self.deck.draw_n(3)
            # resolve the virgin birth
            if self.virgin_birth:
                for i, card in enumerate(drawn_cards):
                    if card.subtype == "virgin_birth":
                        # replace virgin birth with a card from the top 6
                        drawn_cards[i] = self.deck.resolve_the_virgin_birth(
                            drawn_cards[i]
                        )
            self.hand.add(drawn_cards)

        # handle lost souls that are in our hand
        while self.hand.count("lost_soul") > 0:
            # put any lost souls in play
            lost_soul = self.hand.remove("lost_soul")
            self.territory.add(lost_soul)
            # don't draw from empty deck
            if not self.deck.cards_in_deck == 0:
                # then redraw
                self.hand.add(self.deck.draw_n(1))
            if lost_soul.subtype == "cycler":
                # use cycler to dig for macguffin
                if self.hand.count("macguffin") == 0:
                    self.deck.bottom_cards([self.hand.remove("non_lost_soul")])
                    self.hand.add(self.deck.draw_n(1))

        # play macguffin, if we have it
        if self.hand.count("macguffin") > 0:
            self.territory.add(self.hand.remove("macguffin"))
        # if we don't have macguffin, try to tutor for it
        elif self.hand.count("tutor") > 0 and self.deck.count("macguffin") > 0:
            self.territory.add(self.hand.remove("tutor"))
            macguffin_card = self.deck.search_for("macguffin")
            if macguffin_card:
                self.territory.add(macguffin_card)

        # return the turn log
        return {
            "simulation": sim_number,
            "turn": turn_number,
            "n_cards_in_deck": len(self.deck.cards),
            "n_cards_in_hand": len(self.hand.cards),
            "n_lost_souls_in_play": self.territory.count("lost_soul"),
            "n_lost_souls_in_starting_deck": self.souls_in_deck,
            "going_first": self.going_first,
            "macguffin_in_territory": bool(self.territory.count("macguffin")),
            "n_tutors_in_starting_deck": self.n_tutors,
            "deck_size": self.deck_size,
            "n_cycler_souls": self.n_cycler_souls,
            "has_hopper": self.hopper,
        }

    @staticmethod
    def create_empty_log_file():
        """Create empty log file."""
        headers = [
            "simulation",
            "turn",
            "n_cards_in_deck",
            "n_cards_in_hand",
            "n_lost_souls_in_play",
            "n_lost_souls_in_starting_deck",
            "going_first",
            "macguffin_in_territory",
            "n_tutors_in_starting_deck",
            "deck_size",
            "n_cycler_souls",
            "has_hopper",
        ]
        with open("game_log.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

    @staticmethod
    def print_file_size(filename: str):
        """Print the size of a file in bytes."""
        size = os.path.getsize(filename)
        size_kb = size / 1024  # Convert to kilobytes
        print(f"The size of '{filename}' is {size_kb:.2f} kilobytes")

    @staticmethod
    def append_log_to_file(log_data: list[dict], csv_file: str):
        """Bulk add rows of log data to the CSV file."""
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_data[0].keys())
            writer.writerows(log_data)

    def simulate_game(self):
        """Simulate a game of Redemption and record it in a log file."""
        all_logs = []  # Collect all logs to write in bulk
        for sim_number in range(self.n_simulations):
            self.reset_simulation_state()  # Reset deck, hand, discard, and territory

            # draw 8 cards from deck
            self.hand.add(self.deck.draw_n(8))
            # resolve virgin birth star ability
            if virgin_birth := self.hand.search_for(subtype="virgin_birth"):
                self.hand.add(self.deck.resolve_the_virgin_birth(virgin_birth))

            # Log file for the current game simulation
            log_file = []
            for turn_number in range(1, self.n_turns + 1):
                # take a turn
                turn_log = self._take_a_turn(turn_number, sim_number)
                # save the turn log to the current log file
                log_file.append(turn_log)

            # Collect logs instead of writing them immediately
            all_logs.extend(log_file)

        # Bulk write logs at the end of all simulations
        self.append_log_to_file(all_logs, "game_log.csv")
