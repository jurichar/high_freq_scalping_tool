"""
strategy.py

Module for implementing trading strategies.

Functions:
- generate_signals: Generates buy/sell signals based on an optimized strategy.
"""

import numpy as np


def generate_signals(data):
    """
    Generate buy/sell signals based on a combination of technical indicators.

    The strategy uses moving averages crossovers, RSI levels, MACD signals,
    and Bollinger Bands to generate signals.

    Args:
        data (pd.DataFrame): The stock data with technical indicators.

    Returns:
        pd.DataFrame: DataFrame with 'Signal' and 'Filtered_Signal' columns.
    """
    data["Signal"] = 0

    # Moving Averages Crossover
    data["Short_MA"] = data["Close"].rolling(window=50, min_periods=1).mean()
    data["Long_MA"] = data["Close"].rolling(window=200, min_periods=1).mean()
    data["MA_Crossover"] = np.where(data["Short_MA"] > data["Long_MA"], 1, -1)

    # RSI Signals
    data["RSI_Signal"] = np.where(
        data["RSI"] < 30, 1, np.where(data["RSI"] > 70, -1, 0)
    )

    # MACD Signals
    data["MACD_Signal"] = np.where(
        (data["MACD"] > data["MACD_Signal"]),
        1,
        np.where((data["MACD"] < data["MACD_Signal"]), -1, 0),
    )

    # Bollinger Bands Signals
    data["Bollinger_Signal"] = np.where(
        data["Close"] < data["BollingerB_Lower"],
        1,
        np.where(data["Close"] > data["BollingerB_Upper"], -1, 0),
    )

    # Aggregate Signals
    data["Signal"] = (
        data["MA_Crossover"]
        + data["RSI_Signal"]
        + data["MACD_Signal"]
        + data["Bollinger_Signal"]
    )

    data["Filtered_Signal"] = np.where(
        data["Signal"] > 0, 1, np.where(data["Signal"] < 0, -1, 0)
    )

    return data[["Signal", "Filtered_Signal", "Close"]]
