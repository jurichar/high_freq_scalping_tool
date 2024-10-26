"""
data_collector.py

Module for collecting stock data from the Yahoo Finance API using yfinance.

This module provides functions to retrieve historical data
for a specific stock ticker and save the data for further analysis.
"""

import yfinance as yf
import pandas as pd
import os
import logging


def get_stock_data(
    ticker: str,
    period: str = "5d",
    save_to_csv: bool = False,
    output_dir: str = "data/raw/",
    interval: str = "1d",
):
    """
    Retrieve historical data for a given stock ticker
    and optionally save it to a CSV file.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        period (str): The period for which to retrieve data
        (e.g., '5d', '1mo').
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
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)

        if save_to_csv and not data.empty:
            os.makedirs(output_dir, exist_ok=True)
            csv_file = os.path.join(output_dir, f"{ticker}_{period}.csv")
            data.to_csv(csv_file)
            logging.log(f"Data saved to {csv_file}")
    except Exception as e:
        logging.error(f"Error in fetching data: {e}")
        data = pd.DataFrame()
    return data


def get_data_for_period(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    save_to_csv: bool = False,
    output_dir: str = "data/raw/",
):
    """
    Retrieve historical data for a given stock ticker within
    a specified date range.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        start_date (str): The start date for the data (YYYY-MM-DD).
        end_date (str): The end date for the data (YYYY-MM-DD).
        interval (str): The interval for the data (e.g., '1d', '1h').
        save_to_csv (bool): If True, save the data to a CSV file.
        output_dir (str): Directory where the CSV file should be saved.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical stock data.

    Example:
        >>> data = get_data_for_period(
        ...     "MSFT", "2021-01-01", "2021-12-31", interval="1d"
        ... )
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval=interval)

        if save_to_csv and not data.empty:
            os.makedirs(output_dir, exist_ok=True)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")
            csv_file = os.path.join(
                output_dir,
                f"{ticker}_{start_date}_{end_date}.csv",
            )
            data.to_csv(csv_file)
            logging.log(f"Data saved to {csv_file}")
    except Exception as e:
        logging.error(f"Error in fetching data: {e}")
        data = pd.DataFrame()
    return data


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()
    data = get_stock_data("MSFT", "3mo", save_to_csv=True)

    print(data)
