"""
strategy.py

Module for implementing trading strategies.

Functions:
- generate_signals: Generates buy/sell signals based on a simple strategy.
"""


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
    # Calculate moving averages for trend following
    data["Short_MA"] = data["Close"].rolling(window=short_window, min_periods=1).mean()
    data["Long_MA"] = data["Close"].rolling(window=long_window, min_periods=1).mean()

    # Generate initial signals based on moving averages
    data["Signal"] = 0
    data.loc[data["Short_MA"] > data["Long_MA"], "Signal"] = 1
    data.loc[data["Short_MA"] < data["Long_MA"], "Signal"] = -1

    # Enhance signals using RSI for overbought/oversold conditions
    data.loc[data["RSI"] < rsi_threshold, "Signal"] = (
        1  # Buy signal if RSI is below threshold (oversold)
    )
    data.loc[data["RSI"] > (100 - rsi_threshold), "Signal"] = (
        -1
    )  # Sell signal if RSI is above threshold (overbought)

    # Adjust signals using MACD and its signal line
    data.loc[
        (data["MACD"] > macd_threshold) & (data["MACD"] > data["MACD_Signal"]), "Signal"
    ] = 1
    data.loc[
        (data["MACD"] < -macd_threshold) & (data["MACD"] < data["MACD_Signal"]),
        "Signal",
    ] = -1

    # Use Bollinger Bands for detecting breakouts or reversals
    data.loc[data["Close"] < data["BollingerB_Lower"], "Signal"] = (
        1  # Buy if price breaks below lower Bollinger Band
    )
    data.loc[data["Close"] > data["BollingerB_Upper"], "Signal"] = (
        -1
    )  # Sell if price breaks above upper Bollinger Band

    data["Filtered_Signal"] = 0
    data.loc[
        (data["Signal"] == 1) & (data["Close"] > data["EMA"]), "Filtered_Signal"
    ] = 1
    data.loc[
        (data["Signal"] == -1) & (data["Close"] < data["EMA"]), "Filtered_Signal"
    ] = -1

    return data[["Signal", "Filtered_Signal", "Close"]]
