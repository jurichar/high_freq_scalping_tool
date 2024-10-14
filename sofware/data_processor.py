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
- process_data: Cleans data and adds technical indicators.

"""

import logging
import pandas as pd
import os
import pandas_ta as ta

logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data(
    ticker: str = "MSFT", period: str = "3mo", input_dir: str = "data/raw/"
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
        ValueError: If ticker is not alphanumeric or the file is empty or corrupt.
        RuntimeError: For any other errors.

    Tests:
        >>> data = load_data("MSFT", "3mo")
        >>> isinstance(data, pd.DataFrame)
        True
        >>> 'Close' in data.columns
        True
    """
    try:
        if not ticker.isalnum():
            raise ValueError("Ticker symbol must be alphanumeric")

        file_path = os.path.join(input_dir, f"{ticker}_{period}.csv")

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File {file_path} not found. Please run data_collector.py with {ticker} and {period} period."
            )

        data = pd.read_csv(file_path, parse_dates=True, index_col=0)
        return data

    except FileNotFoundError as fnf_error:
        logging.error(fnf_error)
        raise

    except pd.errors.EmptyDataError as ede_error:
        logging.error(f"File {file_path} is empty or corrupt.")
        raise ValueError(f"File {file_path} is empty or corrupt.") from ede_error

    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        raise RuntimeError(f"Error in loading data: {e}") from e


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the stock data by handling missing values.

    - Forward-fill missing values.
    - Drop any remaining missing values.

    Args:
        data (pandas.DataFrame): The raw stock data.

    Returns:
        pandas.DataFrame: A cleaned DataFrame with no missing values.

    Raises:
        ValueError: If input data is not a DataFrame.
        RuntimeError: For unexpected errors.

    Tests:
        >>> raw_data = pd.DataFrame({"Close": [100, None, 102, 0]})
        >>> clean_data(raw_data)['Close'].isnull().sum()
        0
    """
    try:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        data = data.ffill()
        data = data.dropna()
        return data
    except Exception as e:
        logging.error(f"Error in cleaning data: {e}")
        raise RuntimeError(f"Error in cleaning data: {e}") from e


def add_technical_indicators(
    data, sma_period=5, rsi_period=14, bbands_period=20, atr_period=14
) -> pd.DataFrame:
    """
    Add technical indicators to the stock data.

    - Simple Moving Average (SMA).
    - Relative Strength Index (RSI).
    - Moving Average Convergence Divergence (MACD).
    - Bollinger Bands.
    - Exponential Moving Average (EMA).
    - Average True Range (ATR) for risk management.

    Args:
        data (pandas.DataFrame): The cleaned stock data.

    Returns:
        pandas.DataFrame: A DataFrame with added technical indicators.

    Raises:
        ValueError: If input data is not a DataFrame or required columns are missing.
        RuntimeError: For unexpected errors.

    Tests:
        >>> data = pd.DataFrame({"Close": [100, 101, 102, 103, 104],"High": [105, 106, 107, 108, 109],"Low": [95, 96, 97, 98, 99]})
        >>> data_with_indicators = add_technical_indicators(data)
        >>> 'SMA_5' in data_with_indicators.columns
        True
        >>> 'RSI' in data_with_indicators.columns
        True
    """
    try:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        required_columns = ["Close", "High", "Low"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError(
                f"Data must contain the following columns: {', '.join(required_columns)}"
            )

        bbands = ta.bbands(data["Close"], length=bbands_period)

        data[f"SMA_{sma_period}"] = ta.sma(data["Close"], length=sma_period)
        data["RSI"] = ta.rsi(data["Close"], length=rsi_period)

        macd = ta.macd(data["Close"])
        if macd is not None:
            data["MACD"] = macd["MACD_12_26_9"]
            data["MACD_Signal"] = macd["MACDs_12_26_9"]
            data["MACD_Histogram"] = macd["MACDh_12_26_9"]

        if bbands is not None:
            data["BollingerB_Lower"] = bbands[f"BBL_{bbands_period}_2.0"]
            data["BollingerB_Upper"] = bbands[f"BBU_{bbands_period}_2.0"]

        data["EMA"] = ta.ema(data["Close"])
        data["ATR"] = ta.atr(
            data["High"], data["Low"], data["Close"], length=atr_period
        )

        return data

    except Exception as e:
        logging.error(f"Error in adding technical indicators: {e}")
        raise RuntimeError(f"Error in adding technical indicators: {e}") from e


def normalize_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the stock data using Min-Max scaling on selected numeric columns.

    Args:
        data (pandas.DataFrame): The stock data.

    Returns:
        pandas.DataFrame: A DataFrame with normalized stock data.

    Raises:
        ValueError: If input data is not a DataFrame or has no numeric columns.
        RuntimeError: For unexpected errors.

    Tests:
        >>> data = pd.DataFrame({"Close": [100, 101, 102], "Volume": [1000, 1100, 1200]})
        >>> normalized_data = normalize_data(data)
        >>> normalized_data['Close'].min(), normalized_data['Close'].max()
        (0.0, 1.0)
        >>> normalized_data['Volume'].min(), normalized_data['Volume'].max()
        (1000, 1200)
    """
    try:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()

        if not numeric_cols:
            raise ValueError("No numeric columns found for normalization")

        cols_to_exclude = ["Volume", "Dividends", "Stock Splits"]
        cols_to_normalize = [col for col in numeric_cols if col not in cols_to_exclude]

        data[cols_to_normalize] = (
            data[cols_to_normalize] - data[cols_to_normalize].min()
        ) / (data[cols_to_normalize].max() - data[cols_to_normalize].min())
        return data
    except Exception as e:
        logging.error(f"Error in normalizing data: {e}")
        raise RuntimeError(f"Error in normalizing data: {e}") from e


def save_processed_data(
    data: pd.DataFrame,
    ticker: str = "MSFT",
    period: str = "3mo",
    output_dir: str = "data/processed/",
) -> None:
    """
    Save the processed stock data to a CSV file.

    Args:
        data (pandas.DataFrame): The processed stock data.
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.
        output_dir (str): Directory where the CSV file should be saved.

    Raises:
        ValueError: If input data is not a DataFrame.
        RuntimeError: For any file system or I/O errors.

    Tests:
        >>> data = pd.DataFrame({"Close": [100, 101, 102]})
        >>> save_processed_data(data, "MSFT", "3mo")
    """
    try:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{ticker}_{period}_processed.csv")
        data.to_csv(file_path)
    except Exception as e:
        logging.error(f"Error in saving processed data: {e}")
        raise RuntimeError(f"Error in saving processed data: {e}") from e


def process_data(
    data: pd.DataFrame,
    ticker: str = "MSFT",
    period: str = "3mo",
    sma_period=5,
    rsi_period=14,
    bbands_period=20,
    atr_period=14,
) -> pd.DataFrame:
    """
    Process stock data by cleaning and adding technical indicators, then save it.

    Args:
        data (pd.DataFrame): The stock data to process.
        ticker (str): The stock ticker symbol.
        period (str): The period of the data.

    Returns:
        pd.DataFrame: The processed stock data with technical indicators.

    Raises:
        RuntimeError: For any unexpected errors during processing.

    Tests:
        >>> raw_data = pd.DataFrame({"Close": [100, 101, 102], "High": [105, 106, 107], "Low": [95, 96, 97]})
        >>> processed_data = process_data(raw_data, "MSFT", "3mo")
        >>> 'SMA_5' in processed_data.columns
        True
    """
    try:
        data = clean_data(data)
        data = add_technical_indicators(
            data, sma_period, rsi_period, bbands_period, atr_period
        )
        # data = normalize_data(data)  # Uncomment to normalize the data
        save_processed_data(data, ticker, period)
        return data
    except Exception as e:
        logging.error(f"Error in processing data: {e}")
        raise RuntimeError(f"Error in processing data: {e}") from e


# Example usage
if __name__ == "__main__":
    ticker = "MSFT"
    period = "3mo"
    data = load_data(ticker, period)
    process_data(data, ticker, period)
