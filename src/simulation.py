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
    """Class contains all info nessecary to run a simulation."""

    deck: Deck = None
    territory: Territory = None
    hand: Hand = None
    discard: Discard = None

    def __init__(
        self,
        macguffin: str,
        deck_size: int,
        n_cycler_souls: list,
        n_tutors: int,
        n_simulations: int,
        n_turns: int,
        going_first: bool,
        include_hopper: bool,
    ):
        self.macguffin = macguffin
        self.deck_size = deck_size
        self.n_cycler_souls = n_cycler_souls
        self.n_tutors = n_tutors
        self.n_simulations = n_simulations
        self.n_turns = n_turns
        self.going_first = going_first
        self.include_hopper = include_hopper
        self.souls_in_deck = determine_lost_souls_required(deck_size)

    def generate_decklist(
        self,
        deck_size: int = 50,
        n_tutors: int = 0,
        n_cycler_souls: int = 0,
    ) -> deque[Card]:
        """Generate a deck based upon certain parameters."""
        deck_of_cards = deque()

        # Add the macguffin to the deck
        deck_of_cards.append(Card("macguffin"))

        # Add tutors to the deck
        for _ in range(n_tutors):
            deck_of_cards.append(Card("tutor"))

        # Add cycler lost souls to the deck
        for _ in range(n_cycler_souls):
            deck_of_cards.append(Card("lost_soul", subtype="cycler"))

        # Add remaining lost souls to the deck
        for _ in range(self.souls_in_deck - n_cycler_souls):
            deck_of_cards.append(Card("lost_soul", subtype="meek"))

        # Add hopper if included
        if self.include_hopper:
            deck_of_cards.append(Card("lost_soul", subtype="hopper"))

        # Add non-lost_souls to the deck (not including macguffin, tutors, and hopper)
        n_non_lost_souls = (
            deck_size - self.souls_in_deck - n_tutors - int(self.include_hopper) - 1
        )
        for _ in range(n_non_lost_souls):
            deck_of_cards.append(Card("non_lost_soul"))

        return deck_of_cards

    def _take_a_turn(
        self,
        turn_number: int,
        sim_number: int,
    ) -> dict:
        """Take a turn of redemption."""
        # draw 3 cards for turn (except if on the play)
        if not (self.going_first and turn_number == 1):
            drawn_cards = self.deck.draw_n(3)
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
        if self.hand.count("tutor") > 0 and self.deck.count("macguffin") > 0:
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
            "has_hopper": self.include_hopper,
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
    def print_file_size(filename: str) -> None:
        """Print the size of a file in bytes"""
        size = os.path.getsize(filename)
        size_kb = size / 1024  # size in kilobytes
        print(f"The size of '{filename}' is {size_kb} kilobytes")

    @staticmethod
    def append_log_to_file(dict_to_add: list[dict], csv_file: str) -> None:
        """Add a row of log data to the csv file"""
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=dict_to_add[0].keys())
            writer.writerows([row for row in dict_to_add])

    def simulate_game(self) -> None:
        """Simulate a game of Redemption and record it in a log file!"""
        # Create the deck of cards
        decklist = self.generate_decklist(
            deck_size=self.deck_size,
            n_cycler_souls=self.n_cycler_souls,
            n_tutors=self.n_tutors,
        )
        for sim_number in range(self.n_simulations):
            # Create a deck object based on the list of cards we created
            self.deck = Deck(deque(decklist.copy()))
            self.deck.shuffle()

            # create empty zones
            self.territory = Territory(cards=[])
            self.discard = Discard(cards=[])
            self.hand = Hand(cards=[])

            # draw 8 cards from deck
            self.hand.add(self.deck.draw_n(8))

            # Log file for the current game simulation
            log_file = []
            for turn_number in range(1, self.n_turns + 1):
                # take a turn
                turn_log = self._take_a_turn(turn_number, sim_number)
                # save the turn log to the current log file
                log_file.append(turn_log)

            # After all simulations are done, append to the file
            self.append_log_to_file(log_file, "game_log.csv")
