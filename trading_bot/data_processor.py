"""
data_processor.py

Module for cleaning and processing stock data.

This module provides functions to load stock data, clean it, add technical indicators,
normalize the data, and save the processed data.

Functions:
- load_data: Load stock data from a CSV file.
- clean_data: Clean the stock data by handling missing values.
- add_technical_indicators: Add technical indicators like SMA and RSI to the data.
- normalize_data: Normalize the stock data using Min-Max scaling.
- save_processed_data: Save the processed stock data to a CSV file.
"""

import pandas as pd
import os
import pandas_ta as ta
from .data_collector import get_stock_data


def load_data(
    ticker: str, period: str = "1y", input_dir: str = "data/raw/"
) -> pd.DataFrame:
    """
    Load stock data from a CSV file.

    Args:
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.
        input_dir (str): Directory where the CSV file is located.

    Returns:
        pandas.DataFrame: A DataFrame containing the stock data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.

    Example:
        >>> data = load_data("MSFT", "3mo")
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    file_path = os.path.join(input_dir, f"{ticker}_{period}.csv")
    if not os.path.exists(file_path):
        get_stock_data(ticker, period, save_to_csv=True)
        raise FileNotFoundError(f"File {file_path} not found.")
    data = pd.read_csv(
        file_path,
        parse_dates=True,
        index_col=0,
    )
    return data


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the stock data by handling missing values.

    - Forward-fill missing values.
    - Drop any remaining missing values.

    Args:
        data (pandas.DataFrame): The raw stock data.

    Returns:
        pandas.DataFrame: A cleaned DataFrame with no missing values.

    Example:
        >>> raw_data = pd.DataFrame({"Close": [100, None, 102, 0]})
        >>> clean_data(raw_data)['Close'].isnull().sum()
        0
    """
    data = data.ffill()
    data = data.dropna()
    return data


def add_technical_indicators(data, sma_period=5, rsi_period=14, bbands_period=20):
    """
    Add technical indicators to the stock data.

    - Simple Moving Average (SMA) over 5 periods.
    - Relative Strength Index (RSI) over 14 periods.
    - Moving Average Convergence Divergence (MACD).
    - Bollinger Bands.
    - Exponential Moving Average (EMA).

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
    data[f"SMA_{sma_period}"] = ta.sma(data["Close"], length=sma_period)
    data["RSI"] = ta.rsi(data["Close"], length=rsi_period)

    macd = ta.macd(data["Close"])
    if macd is not None:
        data["MACD"] = macd["MACD_12_26_9"]
        data["MACD_Signal"] = macd["MACDs_12_26_9"]
        data["MACD_Histogram"] = macd["MACDh_12_26_9"]

    bbands = ta.bbands(data["Close"], length=bbands_period)
    if bbands is not None:
        lower_band = f"BBL_{bbands_period}_2.0"
        middle_band = f"BBM_{bbands_period}_2.0"
        upper_band = f"BBU_{bbands_period}_2.0"
        data["BollingerB_Lower"] = bbands[lower_band]
        data["BollingerB_Middle"] = bbands[middle_band]
        data["BollingerB_Upper"] = bbands[upper_band]
        data["EMA"] = ta.ema(data["Close"])

    return data


def normalize_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the stock data using Min-Max scaling on selected numeric columns.

    Args:
        data (pandas.DataFrame): The stock data.

    Returns:
        pandas.DataFrame: A DataFrame with normalized stock data.

    Note:
        - Only numeric columns are normalized.
        - Columns 'Dividends', 'Stock Splits', and 'Volume' are excluded from normalization.
        - Non-numeric columns are not affected.

    Example:
        >>> data = pd.DataFrame({"Close": [100, 101, 102], "Volume": [1000, 1100, 1200]})
        >>> normalized_data = normalize_data(data)
        >>> normalized_data['Close'].min(), normalized_data['Close'].max()
        (0.0, 1.0)
        >>> normalized_data['Volume'].min(), normalized_data['Volume'].max()
        (1000, 1200)
    """
    numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()

    cols_to_exclude = ["Volume", "Dividends", "Stock Splits"]
    cols_to_normalize = [col for col in numeric_cols if col not in cols_to_exclude]

    data[cols_to_normalize] = (
        data[cols_to_normalize] - data[cols_to_normalize].min()
    ) / (data[cols_to_normalize].max() - data[cols_to_normalize].min())
    return data


def save_processed_data(
    data: pd.DataFrame,
    ticker: str,
    period: str = "1y",
    output_dir: str = "data/processed/",
) -> None:
    """
    Save the processed stock data to a CSV file.

    Args:
        data (pandas.DataFrame): The processed stock data.
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.
        output_dir (str): Directory where the CSV file should be saved.

    Returns:
        None

    Example:
        >>> data = pd.DataFrame({"Close": [100, 101, 102]})
        >>> save_processed_data(data, "MSFT", "3mo")
    """
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{ticker}_{period}_processed.csv")
    data.to_csv(file_path)


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    ticker = "MSFT"
    period = "1y"
    data = load_data(ticker, period)
    data = normalize_data(data)
    data = add_technical_indicators(data)
    data = clean_data(data)
    save_processed_data(data, ticker, period)
