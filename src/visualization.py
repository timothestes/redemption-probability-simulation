"""
Visualization tools for analyzing and presenting simulation results.

This module is responsible for generating visual representations of the simulation outcomes, 
such as heatmaps showing the probability of certain events occurring under various configurations.
It relies on data produced by the simulation process and uses libraries like 
matplotlib and seaborn to create informative plots.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_simulation_results(
    num_simulations: int,
    going_first: bool,
    hopper: bool,
    deck_size: int,
    virgin_birth: bool,
    prosperity: bool,
    four_drachma_coin: bool,
):
    """Print the results of the simulation as a heatmap."""
    print("creating visualization")
    going_first_status = "True" if going_first else "False"
    hopper_included = "True" if hopper else "False"
    prosperity_included = "True" if prosperity else "False"
    four_drachma_coin = "True" if four_drachma_coin else "False"
    params = {
        "goingfirst": going_first_status,
        "hopper": hopper_included,
        "decksize": deck_size,
        "virgin_birth": virgin_birth,
        "numsims": num_simulations,
        "prosperity": prosperity,
        "four_drachma_coin": four_drachma_coin,
    }

    # Load the simulation results from CSV
    df = pd.read_csv("game_log.csv")

    # Create a new column that includes the deck size label
    df["deck_label"] = f"Deck Size: {deck_size}"

    # Update DataFrame to reflect 'n_cycler_souls' in the y-axis label
    df["n_cycler_souls"] = "Cycler Lost Souls: " + df["n_cycler_souls"].astype(str)

    # Pivot the DataFrame for the heatmap, using 'n_cycler_souls' for the index
    heatmap_data = (
        df.pivot_table(
            index="n_cycler_souls",
            columns="n_tutors_in_starting_deck",
            values="macguffin_in_territory",
            aggfunc="mean",
        )
        * 100
    )

    # Increase the figsize, especially the height
    fig, ax = plt.subplots(figsize=(14, 8))

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        ax=ax,
        linewidths=0.5,
        cbar_kws={"label": "Percentage (%)"},
        vmin=0,  # minimum value of scale
        vmax=100,  # maximum value of scale
    )

    ax.set_ylabel("")
    ax.set_xlabel("Number of Tutors")

    plt.title(
        f"% of Games with Matthew in Play on Turn One ({num_simulations:,} Game Sample Size)",
        fontsize=16,
        fontweight="bold",
        loc="left",
        pad=20,
    )

    plt.tight_layout()
    plt.subplots_adjust(top=0.9, right=0.85)
    conditions_text = (
        f"Going First: {going_first_status}\n"
        f"Hopper Included: {hopper_included}\n"
        f"Prosperity Included {prosperity_included}\n"
        f"Virgin Birth Included: {virgin_birth}\n"
        f"Four-Drachma Coin Included: {four_drachma_coin}\n"
        f"Deck Size: {deck_size}"
    )
    plt.figtext(
        0.82,
        0.5,
        conditions_text,
        ha="left",
        va="center",
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=1"),
    )

    filename = (
        "tmp/simulation_"
        + "_".join(f"{key}-{value}" for key, value in params.items())
        + ".png"
    )

    # Save the figure
    plt.savefig(filename, bbox_inches="tight")

    # Optionally, display the plot
    # plt.show()
