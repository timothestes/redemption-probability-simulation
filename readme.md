# Redemption Probability Simulation

## Overview
This project simulates various scenarios within the Redemption card game, providing insights into the probabilities of specific events occurring based on user-defined simulation parameters. It incorporates Monte Carlo experiment techniques to assess the impact of different variables, such as deck sizes, inclusion of specific cards (e.g., the hopper lost soul), and gameplay strategies, on the game's outcome.

## Features
- Simulation of Redemption card game scenarios with customizable parameters.
- Parsing of command-line arguments to adjust simulation specifics like the number of simulations, tutors, cycler souls, deck size, and game turns.
- Ability to simulate conditions like going first in the game and including special cards (hopper, virgin birth, prosperity, four drachma coin).
- Support for summarizing results into a CSV file for detailed analysis.

## Requirements
- Python 3 installed on the computer.

## Installation
1. Clone the repository to your local machine.
```shell
git clone https://github.com/timothestes/redemption-probability-simulation.git
```
Navigate to the project directory.
```shell
cd redemption-probability-simulation
```
Install the required Python packages.
```shell
sh config.sh
```

## Usage
Navigate to the project root directory and execute the main.py script with desired parameters. Example command:

```shell
python3 -m src.main \
    --n_simulations 5000 \
    --n_tutors_to_try 0 1 2 3 4 5 6 7 8 9 \
    --n_cycler_souls_to_try 0 1 \
    --deck_size 50 \
    --n_turns 1 \
    --going_first \
    --summarize_results
```

## Command-Line Arguments
`--n_simulations`: Number of simulations to run (default: 5000).

`--n_tutors_to_try`: Space-separated list of tutor counts to try in simulations.

`--n_cycler_souls_to_try`: Space-separated list of cycler soul counts to try.

`--deck_size`: Deck size for the simulations (default: 50).

`--n_turns`: Number of turns per simulation (default: 1).

`--going_first`: Flag to simulate going first in the game.

`--summarize_results`: Flag to generate a summary CSV of the results.

## Contributing
Contributions are welcome. Please fork the repository, make your changes, and submit a pull request.

## License
Licensed under the MIT License.