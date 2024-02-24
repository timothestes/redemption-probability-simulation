import pandas as pd


def summarize_results(num_simulations: int):
    """
    Summarize simulation results by calculating the average number of cards seen
    for each unique combination of simulation parameters and export the summary to a CSV file.
    Additionally, include the percentage of games where 'macguffin_in_territory' is true.

    Parameters:
    - num_simulations (int): The number of simulations run.
    """
    chunk_size = 10**6
    chunks = pd.read_csv("game_log.csv", chunksize=chunk_size)

    summary_list = []

    for df in chunks:
        df["macguffin_in_territory"] = df["macguffin_in_territory"].astype(int)

        grouped_df = (
            df.groupby(
                [
                    "going_first",
                    "has_hopper",
                    "has_virgin_birth",
                    "has_prosperity",
                    "has_four_drachma_coin",
                    "has_denarius",
                    "n_cycler_souls",
                    "n_tutors_in_starting_deck",
                ]
            )
            .agg(
                {
                    "n_cards_drawn": "mean",
                    "macguffin_in_territory": ["sum", "count"],
                }
            )
            .reset_index()
        )

        # Flatten multi-level column names if necessary
        grouped_df.columns = [
            "_".join(col).rstrip("_") for col in grouped_df.columns.values
        ]

        summary_list.append(grouped_df)

    # Concatenate chunk summaries
    final_summary_df = pd.concat(summary_list)

    final_aggregated_df = (
        final_summary_df.groupby(
            [
                "going_first",
                "has_hopper",
                "has_virgin_birth",
                "has_prosperity",
                "has_four_drachma_coin",
                "has_denarius",
                "n_cycler_souls",
                "n_tutors_in_starting_deck",
            ]
        )
        .agg(
            {
                "n_cards_drawn_mean": "mean",
                "macguffin_in_territory_sum": "sum",
                "macguffin_in_territory_count": "sum",
            }
        )
        .reset_index()
    )

    # Calculate the percentage of 'macguffin_in_territory'
    final_aggregated_df["percentage_macguffin_in_territory"] = (
        final_aggregated_df["macguffin_in_territory_sum"]
        / final_aggregated_df["macguffin_in_territory_count"]
    ) * 100

    # Drop the now unnecessary columns
    final_aggregated_df.drop(
        columns=[
            "macguffin_in_territory_sum",
            "macguffin_in_territory_count",
        ],
        inplace=True,
    )

    # Rename and cleanup as necessary
    final_aggregated_df.rename(
        columns={"n_cards_drawn_mean": "average_n_cards_drawn"}, inplace=True
    )

    filename_csv = f"tmp/averages_across_{num_simulations}_simulations.csv"
    final_aggregated_df.to_csv(filename_csv, index=False)

    print(f"Summary of results exported to {filename_csv}")
