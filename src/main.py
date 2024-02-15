"""
The main module for the Redemption Probability Simulation project.

This module serves as the entry point for running simulations. 
It parses command-line arguments to configure the simulation parameters, such as the number of 
simulations to run, deck sizes to try, and whether to include specific cards like the hopper. 
It also controls the overall flow of the simulation, including initiating the simulation process 
and potentially generating plots based on the results.
"""

import argparse
import itertools

from src.simulation import Simulation
from src.summarization import summarize_results


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run a simulation of the Redemption card game."
    )
    parser.add_argument(
        "--n_simulations", type=int, default=5000, help="Number of simulations to run."
    )
    parser.add_argument(
        "--n_tutors_to_try",
        nargs="+",
        type=int,
        default=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        help="Number of tutors to try in simulations.",
    )
    parser.add_argument(
        "--n_cycler_souls_to_try",
        nargs="+",
        type=int,
        default=[0, 1],
        help="Number of cycler souls to try in the simulations.",
    )
    parser.add_argument(
        "--deck_size",
        type=int,
        default=50,
        help="Deck size to try in the simulations.",
    )
    parser.add_argument(
        "--n_turns", type=int, default=1, help="Number of turns per simulation."
    )
    parser.add_argument(
        "--going_first",
        action="store_true",
        help="Whether or not you are going first in the game.",
    )
    parser.add_argument(
        "--summarize_results",
        action="store_true",
        help="If flag included, generate a summary csv of the results.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Initialize log file before running simulations
    Simulation.create_empty_log_file()

    boolean_options = [True, False]
    for (
        hopper,
        virgin_birth,
        prosperity,
        four_drachma_coin,
    ) in itertools.product(boolean_options, repeat=4):
        for n_cycler_souls in args.n_cycler_souls_to_try:
            for n_tutors in args.n_tutors_to_try:
                simulation = Simulation(
                    macguffin="Matthew",
                    deck_size=args.deck_size,
                    n_cycler_souls=n_cycler_souls,
                    n_tutors=n_tutors,
                    n_simulations=args.n_simulations,
                    n_turns=args.n_turns,
                    going_first=args.going_first,
                    hopper=hopper,
                    virgin_birth=virgin_birth,
                    prosperity=prosperity,
                    four_drachma_coin=four_drachma_coin,
                )
                simulation.simulate_game()

    # Print file size after all simulations are complete
    simulation.print_file_size("game_log.csv")

    # Generate plot if required
    if args.summarize_results:
        # Adjust parameters as needed to reflect overall simulations
        summarize_results(num_simulations=args.n_simulations)
