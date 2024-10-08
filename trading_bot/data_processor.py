"""
data_processor.py

Module for cleaning and processing stock data.

This module provides functions to clean stock data, add technical indicators, and save the processed data.
"""

import pandas as pd
import os
import pandas_ta as ta


def load_data(
    ticker: str, period: str = "5d", input_dir: str = "data/raw/"
) -> pd.DataFrame:
    """
    Load stock data from a CSV file.

    Args:
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.
        input_dir (str): Directory where the CSV file is located.

    Returns:
        pandas.DataFrame: A DataFrame containing the stock data.

    Example:
        >>> data = load_data("MSFT", "5d")
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    file_path = f"{input_dir}/{ticker}_{period}.csv"
    data = pd.read_csv(file_path, index_col="Date", parse_dates=True)
    return data


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the stock data by filling missing values.

    Args:
        data (pandas.DataFrame): The raw stock data.

    Returns:
        pandas.DataFrame: A cleaned DataFrame with no missing values.

    Example:
        >>> raw_data = pd.DataFrame({"Close": [100, None, 102]})
        >>> clean_data(raw_data)['Close'].isnull().sum()
        0
    """
    data = data.dropna()
    return data


def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the stock data.

    Args:
        data (pandas.DataFrame): The cleaned stock data.

    Returns:
        pandas.DataFrame: A DataFrame with added technical indicators.

    Example:
        >>> data = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})
        >>> data_with_indicators = add_technical_indicators(data)
        >>> 'SMA_5' in data_with_indicators.columns
        True
        >>> 'RSI' in data_with_indicators.columns
        True
    """
    data["SMA_5"] = ta.sma(data["Close"], length=5)
    data["RSI"] = ta.rsi(data["Close"], length=14)
    return data


def save_processed_data(
    data: pd.DataFrame,
    ticker: str,
    period: str = "5d",
    output_dir: str = "data/processed/",
) -> None:
    """
    Save the processed stock data to a CSV file.

    Args:
        data (pandas.DataFrame): The processed stock data.
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.
        output_dir (str): Directory where the CSV file should be saved.

    Example:
        >>> data = pd.DataFrame({"Close": [100, 101, 102]})
        >>> save_processed_data(data, "MSFT", "5d")
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = f"{output_dir}/{ticker}_{period}_processed.csv"
    data.to_csv(file_path)


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    # Load, clean, add indicators, and save data for a given stock
    data = load_data("MSFT", "5d")
    data = clean_data(data)
    data = add_technical_indicators(data)
    save_processed_data(data, "MSFT", "5d")
