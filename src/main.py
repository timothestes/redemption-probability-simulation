"""
The main module for the Redemption Probability Simulation project.

This module serves as the entry point for running simulations. 
It parses command-line arguments to configure the simulation parameters, such as the number of 
simulations to run, deck sizes to try, and whether to include specific cards like the hopper. 
It also controls the overall flow of the simulation, including initiating the simulation process 
and potentially generating plots based on the results.
"""

import argparse

from src.simulation import Simulation
from src.visualization import plot_simulation_results


def parse_args():
    """Function used to parse CLI args."""
    parser = argparse.ArgumentParser(
        description="Run a simulation of the Redemption card game."
    )
    parser.add_argument(
        "--n_simulations",
        type=int,
        default=5000,
        help="Number of simulations to run.",
    )
    parser.add_argument(
        "--n_tutors_to_try",
        nargs="+",
        type=int,
        default=[0, 1, 2, 3, 4, 5, 6, 7, 8],
        help="Number of tutors to try in simulations.",
    )
    parser.add_argument(
        "--n_cycler_souls_to_try",
        nargs="+",
        type=int,
        default=[0, 1, 2],
        help="Number of cycler souls to try in simulations.",
    )
    parser.add_argument(
        "--deck_sizes_to_try",
        nargs="+",
        type=int,
        default=[50],
        help="Deck sizes to try in simulations.",
    )
    parser.add_argument(
        "--n_turns",
        type=int,
        default=1,
        help="Number of turns per simulation.",
    )
    parser.add_argument(
        "--going_first",
        action="store_true",
        help="Whether or not you are going first in the game.",
    )
    parser.add_argument(
        "--include_hopper",
        action="store_true",
        help="Whether or not to include hopper in the deck.",
    )
    parser.add_argument(
        "--generate_plot",
        action="store_true",
        help="If flag included, generate a heatmap of the simulation's results.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Use args to access command-line arguments
    Simulation.create_empty_log_file()
    for deck_size in args.deck_sizes_to_try:
        for n_tutors in args.n_tutors_to_try:
            for n_cycler_souls in args.n_cycler_souls_to_try:
                simulation = Simulation(
                    macguffin="Matthew",
                    deck_size=deck_size,
                    n_cycler_souls=n_cycler_souls,
                    n_tutors=n_tutors,
                    n_simulations=args.n_simulations,
                    n_turns=args.n_turns,
                    going_first=args.going_first,
                    include_hopper=args.include_hopper,
                )
                simulation.simulate_game()
                simulation.print_file_size("game_log.csv")

    if args.generate_plot:
        plot_simulation_results(
            num_simulations=args.n_simulations,
            going_first=args.going_first,
            has_hopper=args.include_hopper,
            deck_size=deck_size,
        )
