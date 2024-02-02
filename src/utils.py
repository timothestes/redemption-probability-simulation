"""
Utility functions for the Redemption Probability Simulation project.

This module provides helper functions that are used across the simulation project, 
such as determining the required number of Lost Souls cards based on the deck size.
These functions support various aspects of the simulation and data processing tasks.
"""


def determine_lost_souls_required(deck_size: int):
    """Determine the number of Lost Souls required based on the deck size."""
    if 50 <= deck_size <= 56:
        return 7
    elif 57 <= deck_size <= 63:
        return 8
    elif 64 <= deck_size <= 70:
        return 9
    elif 71 <= deck_size <= 77:
        return 10
    elif 78 <= deck_size <= 84:
        return 11
    elif 85 <= deck_size <= 91:
        return 12
    elif 92 <= deck_size <= 98:
        return 13
    elif 99 <= deck_size <= 105:
        return 14
    else:
        raise ValueError("Deck size out of range for Lost Souls calculation")
