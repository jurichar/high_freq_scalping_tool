"""
strategy.py

Module for implementing scalping trading strategies.

Functions:
- generate_signals: Generates buy/sell signals based on a scalping strategy.
"""

import numpy as np
import pandas as pd


def generate_signals(data):
    """
    Generate buy/sell signals based on a scalping strategy.

    The strategy uses short-term EMA crossovers, RSI levels,
    Bollinger Bands, and ATR for volatility-adjusted stop-losses.

    Args:
        data (pd.DataFrame): The stock data with technical indicators.

    Returns:
        pd.DataFrame: DataFrame with 'Signal' and 'Close' columns.
    """

    # Ensure data is sorted by date
    data = data.sort_index()

    # Short-term EMAs
    data["EMA_5"] = data["Close"].ewm(span=5, adjust=False).mean()
    data["EMA_10"] = data["Close"].ewm(span=10, adjust=False).mean()

    # EMA Crossover Signal
    data["EMA_Signal"] = 0
    data["EMA_Signal"] = np.where(data["EMA_5"] > data["EMA_10"], 1, -1)

    # Short-term RSI
    data["RSI_Short"] = data["RSI"].rolling(window=7).mean()

    # RSI Signal
    data["RSI_Signal"] = 0
    data["RSI_Signal"] = np.where(
        data["RSI_Short"] < 30, 1, np.where(data["RSI_Short"] > 70, -1, 0)
    )

    # Bollinger Bands Signal
    data["BB_Signal"] = 0
    data["BB_Signal"] = np.where(
        data["Close"] < data["BollingerB_Lower"],
        1,
        np.where(data["Close"] > data["BollingerB_Upper"], -1, 0),
    )

    # Aggregate Signals
    data["Signal"] = data["EMA_Signal"] + data["RSI_Signal"] + data["BB_Signal"]

    # Final Signal
    data["Signal"] = np.where(
        data["Signal"] > 0, 1, np.where(data["Signal"] < 0, -1, 0)
    )

    # Filter duplicate signals
    data["Signal"] = data["Signal"].diff().fillna(data["Signal"])

    # Adjust stop-loss and take-profit using ATR
    data["ATR_Stop_Loss"] = data["ATR"] * 1.5  # Multiplier can be adjusted
    data["ATR_Take_Profit"] = data["ATR"] * 2  # Multiplier can be adjusted

    return data[["Signal", "Close", "High", "Low", "ATR_Stop_Loss", "ATR_Take_Profit"]]
