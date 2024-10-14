"""
plot_draws.py


"""

import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(equity_curve):
    """
    Plots the equity curve over time.

    Args:
        equity_curve (pd.Series): The equity curve of the portfolio.
    """
    plt.figure(figsize=(14, 7))
    equity_curve.plot()
    plt.title("Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    plt.show()


def plot_drawdown(equity_curve):
    """
    Plots the drawdown over time.

    Args:
        equity_curve (pd.Series): The equity curve of the portfolio.
    """
    drawdown = (equity_curve / equity_curve.cummax()) - 1
    plt.figure(figsize=(14, 7))
    drawdown.plot()
    plt.title("Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown (%)")
    plt.grid(True)
    plt.show()


def plot_atr(data):
    """
    Plots the Average True Range (ATR) over time.

    Args:
        data (pd.DataFrame): The stock data with ATR values.
    """
    plt.figure(figsize=(21, 7))
    plt.plot(data.index, data["ATR"], label="ATR")
    plt.title("Average True Range (ATR)", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("ATR Value", fontsize=14)
    plt.legend()
    plt.show()


def plot_rsi(data):
    """
    Plots the Relative Strength Index (RSI) over time.

    Args:
        data (pd.DataFrame): The stock data with RSI values.
    """
    plt.figure(figsize=(21, 7))
    plt.plot(data.index, data["RSI"], label="RSI")
    plt.axhline(30, linestyle="--", alpha=0.5, color="red", label="Oversold Level (30)")
    plt.axhline(
        70, linestyle="--", alpha=0.5, color="green", label="Overbought Level (70)"
    )
    plt.title("RSI Indicator", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("RSI Value")
    plt.legend()
    plt.show()


def plot_bollinger_bands(data):
    """
    Plots the Bollinger Bands over time.

    Args:
        data (pd.DataFrame): The stock data with Bollinger Bands values.
    """
    plt.figure(figsize=(21, 7))
    plt.fill_between(
        data.index,
        data["BollingerB_Lower"],
        data["BollingerB_Upper"],
        color="gray",
        alpha=0.15,
        label="Bollinger Bands",
    )
    plt.plot(data["Close"], label="Close Price")
    plt.plot(data["BollingerB_Lower"], linestyle="--", color="red", label="Lower Band")
    plt.plot(
        data["BollingerB_Upper"], linestyle="--", color="green", label="Upper Band"
    )
    plt.title("Bollinger Bands", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Price", fontsize=14)
    plt.legend()
    plt.show()


def plot_ema_and_sma(data):
    plt.figure(figsize=(21, 7))
    plt.plot(data.index, data["Close"], label="Close Price")
    plt.plot(
        data.index, data["SMA_5"], label="5-Day SMA", color="green", linestyle="--"
    )
    plt.plot(data.index, data["EMA"], label="EMA", color="orange", linestyle="--")
    plt.title("Close Price with SMA and EMA", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.show()
