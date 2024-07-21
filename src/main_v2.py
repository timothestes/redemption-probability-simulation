"""PENDING
"""

import argparse

from src.spectrograph_simulation import SpectrographSimulation
from src.utils import float_between_0_and_1


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="PENDING")
    parser.add_argument(
        "--n_simulations", type=int, default=50, help="Number of simulations to run."
    )
    parser.add_argument(
        "--deck_file_path",
        type=str,
        help="The path to your deck file (txt) relative to this module.",
    )
    parser.add_argument(
        "--cycler_logic",
        default="random",
        help="If flag specified, controls the behavior of the cylcer souls.",
    )
    parser.add_argument(
        "--crowds_ineffectiveness_weight",
        type=float_between_0_and_1,
        default=0.6,
        help="The percent of times you think Matthew decks will be able to answer the crowds lost soul. Must be a number between 0 and 1",
    )
    parser.add_argument(
        "--matthew_fizzle_rate",
        type=float_between_0_and_1,
        default=0.15,
        help="The percent of times you think Matthew decks will not be able to put matthew into play on turn one",
    )
    parser.add_argument
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Initialize log file before running simulations
    SpectrographSimulation.create_empty_log_file()

    simulation = SpectrographSimulation(
        deck_file_path=args.deck_file_path,
        n_simulations=args.n_simulations,
        cycler_logic=args.cycler_logic,
        crowds_ineffectiveness_weight=args.crowds_ineffectiveness_weight,
        matthew_fizzle_rate=args.matthew_fizzle_rate,
    )
    simulation.initialize_decklist()
    simulation.run()
    simulation.print_results()
