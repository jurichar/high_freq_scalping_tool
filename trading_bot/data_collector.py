"""
data_collector.py

Module for collecting stock data from the Yahoo Finance API using yfinance.

This module provides functions to retrieve historical data for a specific stock ticker and save the data for further analysis.
"""

import yfinance as yf
import pandas as pd
import os


def get_stock_data(
    ticker: str,
    period: str = "5d",
    save_to_csv: bool = False,
    output_dir: str = "data/raw/",
):
    """
    Retrieve historical data for a given stock ticker and optionally save it to a CSV file.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        period (str): The period for which to retrieve data (e.g., '5d', '1mo').
        save_to_csv (bool): If True, save the data to a CSV file.
        output_dir (str): Directory where the CSV file should be saved.

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

    if save_to_csv:
        os.makedirs(output_dir, exist_ok=True)
        csv_file = os.path.join(output_dir, f"{ticker}_{period}.csv")
        data.to_csv(csv_file)
        print(f"Data saved to {csv_file}")

    return data


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()
    data = get_stock_data("MSFT", "3mo", save_to_csv=True)
    print(data)
