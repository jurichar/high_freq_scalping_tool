"""
utils.py

Module containing utility functions for the software.
"""

import logging

import pandas as pd


def validate_data(data):
    """
    Validate the input data for analysis.

    Args:
        data (pd.DataFrame): Dataframe containing the historical prices.

    Returns:
        bool: True if the data is valid, False otherwise.

    Example:
        >>> data = pd.DataFrame({'Close': [100, 101, 102]})
        >>> validate_data(data)
        True
        >>> validate_data(None)
        False
    """

    if not isinstance(data, pd.DataFrame) or data.empty:
        logging.error("Invalid or empty data.")
        return False
    return True
