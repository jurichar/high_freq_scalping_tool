'''
File: utils.py
Project: software
File Created: Monday, 7th October 2024 5:36:25 pm
Author: Julien RICHARD (jurichar@student.42.fr)
-----
Last Modified: Friday, 29th November 2024 1:31:28 am
Modified By: Julien RICHARD (jurichar@student.42.fr>)
-----
Copyright 2017 - 2024 jurichar
'''


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
