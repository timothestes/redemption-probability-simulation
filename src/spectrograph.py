"""The module for the spectrograph tool that will tell you how many cards an opposing Matthew
will draw on average for a given deck file.
"""

import argparse

from src.spectrograph_simulation import SpectrographSimulation


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run an analysis on a deck of Redemption cards to find out number of cards an opposing Matthew might draw."
    )
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
        help="If flag specified, controls the behavior of the cylcer souls. Setting to underdeck_colors will attempt to underdeck the cards in your hand that have the most colors.",
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
    )
    simulation.initialize_decklist()
    simulation.run()
    simulation.print_results()
