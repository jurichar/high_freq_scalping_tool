"""
data_collector.py

Module for collecting stock data from the Yahoo Finance API using yfinance.

This module provides functions to retrieve historical data for a specific stock ticker and save the data for further analysis.
"""

import yfinance as yf
import pandas as pd
import os


def is_data_cached(ticker: str, period: str, output_dir: str = "data/raw/") -> bool:
    """
    Check if the stock data is already cached in the specified directory.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'MSFT').
        period (str): The period for which to retrieve data (e.g., '5d', '1mo').
        output_dir (str): Directory where the CSV file should be saved.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    csv_file = os.path.join(output_dir, f"{ticker}_{period}.csv")
    return os.path.exists(csv_file)


def get_stock_data(
    ticker: str,
    period: str = "5d",
    save_to_csv: bool = False,
    output_dir: str = "data/raw/",
    interval: str = "1d",
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
    try:
        if is_data_cached(ticker, period, output_dir):
            return pd.read_csv(
                os.path.join(output_dir, f"{ticker}_{period}.csv"),
                index_col=0,
                parse_dates=True,
            )

        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)

        if save_to_csv:
            os.makedirs(output_dir, exist_ok=True)
            csv_file = os.path.join(output_dir, f"{ticker}_{period}.csv")
            data.to_csv(csv_file)
            print(f"Data saved to {csv_file}")
    except Exception as e:
        print(f"Error in fetching data: {e}")
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
    Retrieve historical data for a given stock ticker within a specified date range.

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
        >>> data = get_data_for_period("MSFT", "2021-01-01", "2021-12-31", interval="1d")
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        period = f"{start_date.date()}:{end_date.date()}"
        data = get_stock_data(
            ticker,
            period=period,
            save_to_csv=save_to_csv,
            output_dir=output_dir,
            interval=interval,
        )
    except Exception as e:
        print(f"Error in fetching data: {e}")
        data = pd.DataFrame()
    return data


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()
    data = get_stock_data("MSFT", "3mo", save_to_csv=True)

    print(data)
