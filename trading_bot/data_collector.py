"""
data_collector.py

Module for collecting stock data from the Yahoo Finance API using yfinance.

This module provides functions to retrieve historical data for a specific stock ticker and save the data for further analysis.
"""

import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str, period: str = "5d"):
    """
    Retrieve historical data for a given stock ticker.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        period (str): The period for which to retrieve data (e.g., '5d', '1mo').

    Returns:
        pandas.DataFrame: A DataFrame containing the historical stock data.

    Example:
        >>> data = get_stock_data("MSFT", "5d")
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()
    data = get_stock_data("MSFT", "5d")
    print(data)
