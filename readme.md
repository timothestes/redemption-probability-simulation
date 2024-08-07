# Redemption Probability Simulation

## Overview
This project simulates various scenarios within the Redemption card game, providing insights into the probabilities of specific events occurring based on user-defined simulation parameters. It incorporates Monte Carlo experiment techniques to assess the impact of different variables, such as deck sizes, inclusion of specific cards (e.g., the hopper lost soul), and gameplay strategies, on the game's outcome.

## Features (simulation.py)
- Simulation of Redemption card game scenarios with customizable parameters.
- Parsing of command-line arguments to adjust simulation specifics like the number of simulations, tutors, cycler souls, deck size, and game turns.
- Ability to simulate conditions like going first in the game and including special cards (hopper, virgin birth, prosperity, four drachma coin).
- Support for summarizing results into a CSV file for detailed analysis.

## Features (spectrograph.py)
- Spectrograph: Ability to simulat the number of brigades an opposing Matthew would draw if they went first.


## Requirements
- Python 3 installed on the computer.
- Lackey installed with the Redemption Plugin

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
1) Copy your Redemption decklist in lackey and put it into a `.txt` file. Note its path for step 2.

2) Navigate to the project root directory and execute the spectogrpah.py script with desired parameters. Example command:

```shell
python3 -m src.spectrograph \
    --n_simulations 100000 \
    --deck_file_path decks/test_dummy_deck.txt \
    --crowds_ineffectiveness_weight .6 \
    --matthew_fizzle_rate .15
```

## Command-Line Arguments
`--n_simulations`: Number of simulations to run.

`--deck_file_path`: The path to where your Redemption decklist is at.

`--crowds_ineffectiveness_weight`: A number between 0 and 1 that helps the simulation factor in the times Matthew decks will have an answer to the Crowds lost soul. The value 1 would mean that crowds would be ineffective 100% of the time (meaning it would never work), .6 would mean that crowds would ineffecive 60% of the time, etc. Defaults to .6. If you aren't playing Crowds lost soul in your deck, this number has no effect on the simulation. 

`--cycler_logic`: Determines the logic for resolving the Cycler Souls, Prosperity, and Virgin Birth cards. Can be set to `random` or `optimized`. Defaults to `random`. Optimized will underdeck/discard cards with the most brigades.

`--matthew_fizzle_rate`: A number between 0 and 1 that helps the simulation factor in the times Matthew decks will not have a Matthew on Turn 1. The value 1 would mean that they would would not have Matthew Turn 1 100% of the time, .6 would mean that they don't have Matthew 60% of the time, etc. Defaults to .15 (they fizzle only 15% of the time)

## Notes:
If running on a windows computer, you'll have to change a variable in `src/decklist.py`
Change the `self.card_data_path` to the directory where your lackey's `carddata.txt` lives
```python
self.card_data_path = (
    "/Applications/LackeyCCG/plugins/Redemption/sets/carddata.txt" -> change to where the file actually lives
)
```

## Contributing
Contributions are welcome. Please fork the repository, make your changes, and submit a pull request.

## License
Licensed under the MIT License.