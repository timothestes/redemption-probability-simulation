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
        prosperity: bool,
        four_drachma_coin: bool,
        denarius: bool,
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
        self.prosperity = prosperity
        self.four_drachma_coin = four_drachma_coin
        self.denarius = denarius
        self.souls_in_deck = determine_lost_souls_required(deck_size)
        # prosperity and n_cycler_souls subtract from the number of other souls in the deck.
        self.modified_souls_in_deck = (
            self.souls_in_deck - int(prosperity) - n_cycler_souls
        )
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

        # add lost souls
        if self.hopper:
            deck_of_cards.append(Card("lost_soul", subtype="hopper"))
        if self.prosperity:
            deck_of_cards.append(Card("lost_soul", subtype="prosperity"))
        if self.n_cycler_souls:
            deck_of_cards.extend(
                [
                    Card("lost_soul", subtype="cycler")
                    for _ in range(self.n_cycler_souls)
                ]
            )
        deck_of_cards.extend(
            [
                Card("lost_soul", subtype="meek")
                for _ in range(self.modified_souls_in_deck)
            ]
        )

        # add other cards
        if self.virgin_birth:
            deck_of_cards.append(Card("non_lost_soul", subtype="virgin_birth"))
        if self.four_drachma_coin:
            # add peter and four-drachma coin to the deck
            deck_of_cards.append(Card("non_lost_soul", subtype="peter"))
            deck_of_cards.append(Card("non_lost_soul", subtype="coin"))
        if self.denarius:
            # add denarious and one roman emperor to the deck
            deck_of_cards.append(Card("non_lost_soul", subtype="denarius"))
            deck_of_cards.append(Card("non_lost_soul", subtype="emperor"))

        # fill the rest with chaff
        other_cards = self.deck_size - len(deck_of_cards)
        deck_of_cards.extend([Card("non_lost_soul") for _ in range(other_cards)])

        return deck_of_cards

    def reset_simulation_state(self):
        """Reset the state of the simulation for a new run."""
        self.deck.reset(shuffle=True)
        self.territory.reset()
        self.discard.reset()
        self.hand.reset()

    def _play_drachma_coin_cards(self):
        """Play out peter and four drachma coin."""
        # play peter
        if self.hand.count(subtype="peter") > 0:
            self.territory.add(self.hand.remove(subtype="peter"))
        # play coin
        if self.hand.count(subtype="coin") > 0:
            self.territory.add(self.hand.remove(subtype="coin"))
        # if we have coin and peter in play, discard coin to draw 4
        if (
            self.territory.count(subtype="coin") > 0
            and self.territory.count(subtype="peter") > 0
        ):
            self.discard.add(self.territory.remove(subtype="coin"))
            self._draw_cards(n_cards=4, resolve_stars=False)
            # play any cards drawn
            self._play_draw_cards()

    def _play_denarius_cards(self):
        """Play out the denarius cards."""
        # play denarius
        if self.hand.count(subtype="denarius") > 0:
            self.territory.add(self.hand.remove(subtype="denarius"))
            # search deck for an emperor
            if self.deck.count(subtype="emperor") > 0:
                self.hand.add(self.deck.search_for(subtype="emperor"))
        # play emperor
        if self.hand.count(subtype="emperor") > 0:
            self.territory.add(self.hand.remove(subtype="emperor"))

        # check to see if we have both in play
        if (
            self.territory.count(subtype="denarius") == 1
            and self.territory.count(subtype="emperor") > 0
        ):
            # if we have denarius and at least one emperor, discard denarius to draw 3
            self.discard.add(self.territory.remove(subtype="denarius"))
            self._draw_cards(n_cards=3, resolve_stars=False)
            # play any cards drawn
            self._play_draw_cards()

    def _play_draw_cards(self):
        """Play cards out of our hand."""
        if self.four_drachma_coin:
            self._play_drachma_coin_cards()
        if self.denarius:
            self._play_denarius_cards()

    def _play_macguffin(self):
        """Play the macguffin if we have it."""
        if self.hand.count("macguffin") > 0:
            self.territory.add(self.hand.remove("macguffin"))
        # if we don't have macguffin, try to tutor for it
        elif self.hand.count("tutor") > 0 and self.deck.count("macguffin") > 0:
            self.territory.add(self.hand.remove("tutor"))
            macguffin_card = self.deck.search_for("macguffin")
            if macguffin_card:
                self.territory.add(macguffin_card)

    def _draw_cards(self, n_cards: int, resolve_stars=False):
        """Handle anytime we draw cards during the game."""
        drawn_cards = self.deck.draw_n(n_cards)

        if resolve_stars:
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
                if self.hand.count("macguffin") == 0 and self.hand.count("tutor") == 0:
                    # TODO: this will currently underdeck peter and coin, but we want to prioritize underdeck... please implement a hand.smart_choose function
                    self.deck.bottom_cards([self.hand.remove("non_lost_soul")])
                    self.hand.add(self.deck.draw_n(1))
            elif lost_soul.subtype == "prosperity":
                # use prosperity to dig for macguffin
                if self.hand.count("macguffin") == 0 and self.hand.count("tutor") == 0:
                    # TODO: this will currently discard peter and coin, but we want to prioritize discarding... please implement a hand.smart_choose function
                    self.discard.add(self.hand.remove("non_lost_soul"))
                    self.hand.add(self.deck.draw_n(2))

    def _take_a_turn(
        self,
        turn_number: int,
        sim_number: int,
    ) -> dict:
        """Take a turn of redemption."""
        # draw 3 cards for turn (except if on the play), resolve star abilites
        if not (self.going_first and turn_number == 1):
            self._draw_cards(n_cards=3, resolve_stars=True)

        # play any relevant cards in our hand.
        self._play_draw_cards()

        self._play_macguffin()

        # return the turn log
        return {
            # "simulation": sim_number,
            # "turn": turn_number,
            # "n_cards_left_in_deck": len(self.deck.cards),
            "n_cards_drawn": self.deck_size - len(self.deck.cards),
            # "n_cards_in_hand": len(self.hand.cards),
            # "n_lost_souls_in_play": self.territory.count("lost_soul"),
            # "n_lost_souls_in_starting_deck": self.souls_in_deck,
            "going_first": self.going_first,
            "macguffin_in_territory": bool(self.territory.count("macguffin")),
            "n_tutors_in_starting_deck": self.n_tutors,
            # "deck_size": self.deck_size,
            "n_cycler_souls": self.n_cycler_souls,
            "has_virgin_birth": self.virgin_birth,
            "has_hopper": self.hopper,
            "has_prosperity": self.prosperity,
            "has_four_drachma_coin": self.four_drachma_coin,
            "has_denarius": self.denarius,
        }

    @staticmethod
    def create_empty_log_file():
        """Create empty log file."""
        headers = [
            # "simulation",
            # "turn",
            # "n_cards_left_in_deck",
            "n_cards_drawn",
            # "n_cards_in_hand",
            # "n_lost_souls_in_play",
            # "n_lost_souls_in_starting_deck",
            "going_first",
            "macguffin_in_territory",
            "n_tutors_in_starting_deck",
            # "deck_size",
            "n_cycler_souls",
            "has_virgin_birth",
            "has_hopper",
            "has_prosperity",
            "has_four_drachma_coin",
            "has_denarius",
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
            self._draw_cards(n_cards=8, resolve_stars=True)

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
