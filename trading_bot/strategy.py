"""
strategy.py

Module for implementing trading strategies.

Functions:
- generate_signals: Generates buy/sell signals based on a simple strategy.
"""

import numpy as np


def generate_signals(
    data, short_window=50, long_window=200, rsi_threshold=30, macd_threshold=0
):
    """
    Generates trading signals (buy/sell) based on moving averages, RSI, MACD, and Bollinger Bands.

    Args:
        data (pd.DataFrame): The stock data with technical indicators.
        short_window (int): The window size for the short-term moving average.
        long_window (int): The window size for the long-term moving average.
        rsi_threshold (int): The RSI threshold for buy/sell signals.
        macd_threshold (float): The MACD threshold for buy/sell signals.

    Returns:
        pd.DataFrame: DataFrame with 'Signal' column indicating buy/sell actions.
    """
    data["Short_MA"] = data["Close"].rolling(window=short_window, min_periods=1).mean()
    data["Long_MA"] = data["Close"].rolling(window=long_window, min_periods=1).mean()
    data["Signal"] = 0

    conditions = [
        (data["Short_MA"] > data["Long_MA"]),
        (data["Short_MA"] < data["Long_MA"]),
        (data["RSI"] < rsi_threshold),
        (data["RSI"] > (100 - rsi_threshold)),
        ((data["MACD"] > macd_threshold) & (data["MACD"] > data["MACD_Signal"])),
        ((data["MACD"] < -macd_threshold) & (data["MACD"] < data["MACD_Signal"])),
        (data["Close"] < data["BollingerB_Lower"]),
        (data["Close"] > data["BollingerB_Upper"]),
    ]

    choices = [1, -1, 1, -1, 1, -1, 1, -1]

    for condition, choice in zip(conditions, choices):
        data["Signal"] = np.where(condition, choice, data["Signal"])

    data["Filtered_Signal"] = 0
    buy_condition = (data["Signal"] == 1) & (data["Close"] > data["EMA"])
    sell_condition = (data["Signal"] == -1) & (data["Close"] < data["EMA"])
    data["Filtered_Signal"] = np.where(buy_condition, 1, data["Filtered_Signal"])
    data["Filtered_Signal"] = np.where(sell_condition, -1, data["Filtered_Signal"])

    return data[["Signal", "Filtered_Signal", "Close"]]
