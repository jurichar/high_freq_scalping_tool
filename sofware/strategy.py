"""
strategy.py

Module for implementing scalping trading strategies.

Functions:
- generate_signals: Generates buy/sell signals based on a scalping strategy.
"""

import numpy as np
import pandas as pd


def generate_signals(data, ema_short=5, ema_long=10, rsi_period=7, bbands_period=20):
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
    data[f"EMA_{ema_short}"] = data["Close"].ewm(span=ema_short, adjust=False).mean()
    data[f"EMA_{ema_long}"] = data["Close"].ewm(span=ema_long, adjust=False).mean()

    # EMA Crossover Signal
    data["EMA_Signal"] = 0
    data["EMA_Signal"] = np.where(
        data[f"EMA_{ema_short}"] > data[f"EMA_{ema_long}"], 1, -1
    )

    # Short-term RSI
    data["RSI_Short"] = data["RSI"].rolling(window=rsi_period).mean()

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

    # MACD Signal
    data["MACD_Signal_Strength"] = np.where(
        (data["MACD"] > data["MACD_Signal"]),
        1,
        np.where((data["MACD"] < data["MACD_Signal"]), -1, 0),
    )

    # Assign weights to each signal
    weights = {
        "EMA_Signal": 2,
        "RSI_Signal": 1,
        "BB_Signal": 1,
        "MACD_Signal_Strength": 1,
    }

    # Vectorize signal score calculation using np.dot for efficiency
    signal_columns = ["EMA_Signal", "RSI_Signal", "BB_Signal", "MACD_Signal_Strength"]
    signal_weights = np.array([weights[col] for col in signal_columns])
    data["Signal_Score"] = np.dot(data[signal_columns].values, signal_weights)

    # Define final signal based on threshold
    data["Signal"] = np.where(
        data["Signal_Score"] >= 3, 1, np.where(data["Signal_Score"] <= -3, -1, 0)
    )

    # Filter duplicate signals
    data["Signal"] = data["Signal"].diff().fillna(data["Signal"])

    # Adjust stop-loss and take-profit using ATR
    data["ATR_Stop_Loss"] = data["ATR"] * 1.5
    data["ATR_Take_Profit"] = data["ATR"] * 3

    data = data.dropna(
        subset=["ATR_Stop_Loss", "ATR_Take_Profit", "MACD", "MACD_Signal"]
    )

    return data[["Signal", "Close", "High", "Low", "ATR_Stop_Loss", "ATR_Take_Profit"]]
