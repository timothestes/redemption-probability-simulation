import pandas as pd


def summarize_results(num_simulations: int):
    """
    Summarize simulation results by calculating the average number of cards seen
    for each unique combination of simulation parameters and export the summary to a CSV file.
    Additionally, include the percentage of games where 'macguffin_in_territory' is true.

    Parameters:
    - num_simulations (int): The number of simulations run.
    """
    chunk_size = 10**6  # Define a suitable chunk size
    chunks = pd.read_csv("game_log.csv", chunksize=chunk_size)

    summary_list = []  # Initialize an empty list to store summary data from each chunk

    for df in chunks:
        # Convert 'macguffin_in_territory' to integer (1 for True, 0 for False)
        df["macguffin_in_territory"] = df["macguffin_in_territory"].astype(int)

        # Group and aggregate data within each chunk
        grouped_df = (
            df.groupby(
                [
                    "going_first",
                    "has_hopper",
                    "has_virgin_birth",
                    "has_prosperity",
                    "has_four_drachma_coin",
                    "deck_size",
                    "n_cycler_souls",
                    "n_tutors_in_starting_deck",
                ]
            )
            .agg(
                {
                    "cards_seen": "mean",
                    "macguffin_in_territory": "mean",
                }
            )
            .reset_index()
        )

        # Convert the 'macguffin_in_territory' mean to a percentage
        grouped_df["macguffin_in_territory"] *= 100

        # Append the grouped data to the list
        summary_list.append(grouped_df)

    # Concatenate all chunk summaries into a single DataFrame
    final_summary_df = pd.concat(summary_list)

    # Further group by and aggregate to account for potential overlaps between chunks
    final_summary_df = (
        final_summary_df.groupby(
            [
                "going_first",
                "has_hopper",
                "has_virgin_birth",
                "has_prosperity",
                "has_four_drachma_coin",
                "deck_size",
                "n_cycler_souls",
                "n_tutors_in_starting_deck",
            ]
        )
        .agg(
            {
                "cards_seen": "mean",
                "macguffin_in_territory": "mean",
            }
        )
        .reset_index()
    )

    # Rename columns for clarity
    final_summary_df.rename(
        columns={
            "cards_seen": "average_cards_seen",
            "macguffin_in_territory": "percentage_macguffin_in_territory",
        },
        inplace=True,
    )

    # Define the filename to include the number of simulations for better traceability
    filename_csv = f"tmp/average_cards_seen_per_game_{num_simulations}_simulations.csv"
    # Export the final summary to a CSV file
    final_summary_df.to_csv(filename_csv, index=False)

    print(f"Summary of results exported to {filename_csv}")
