'''
File: plotter.py
Project: software
File Created: Tuesday, 15th October 2024 12:10:30 am
Author: Julien RICHARD (jurichar@student.42.fr)
-----
Last Modified: Friday, 29th November 2024 1:30:21 am
Modified By: Julien RICHARD (jurichar@student.42.fr>)
-----
Copyright 2017 - 2024 jurichar
'''

import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(date, equity_curve):
    """
    Plots the equity curve over time.

    Args:
        equity_curve (pd.Series): The equity curve of the portfolio.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(date, equity_curve)
    plt.title("Equity Curve", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Portfolio Value ($)", fontsize=14)
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
    plt.title("Drawdown", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Drawdown (%)", fontsize=14)
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
    plt.grid(True)
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
    plt.axhline(
        30, linestyle="--", alpha=0.5, color="red", label="Oversold Level (30)"
    )
    plt.axhline(
        70,
        linestyle="--",
        alpha=0.5,
        color="green",
        label="Overbought Level (70)",
    )
    plt.title("RSI Indicator", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("RSI Value", fontsize=14)
    plt.grid(True)
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
    plt.plot(
        data["BollingerB_Lower"],
        linestyle="--",
        color="red",
        label="Lower Band",
    )
    plt.plot(
        data["BollingerB_Upper"],
        linestyle="--",
        color="green",
        label="Upper Band",
    )
    plt.title("Bollinger Bands", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Price", fontsize=14)
    plt.grid(True)
    plt.legend()
    plt.show()


def plot_ema_and_sma(data):
    plt.figure(figsize=(21, 7))
    plt.plot(data.index, data["Close"], label="Close Price")
    plt.plot(
        data.index, data["SMA"], label="SMA", color="green", linestyle="--"
    )
    plt.plot(
        data.index, data["EMA"], label="EMA", color="orange", linestyle="--"
    )
    plt.title("Close Price with SMA and EMA", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Price", fontsize=14)
    plt.grid(True)
    plt.legend()
    plt.show()


def plot_signals(data):
    """
    Plots the close prices and overlays buy/sell signals on the chart.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'Close' prices and 'Signal' column.
    """
    buy_short = data["Signal"] == -1
    buy_long = data["Signal"] == 1

    plt.figure(figsize=(14, 7))
    plt.title("Buy Signals", fontsize=16)
    plt.plot(data.index, data["Close"], label="Close Price", lw=1.5)
    if buy_short.any():
        plt.plot(
            data.index[buy_short],
            data["Close"][buy_short],
            "v",
            markersize=8,
            color="red",
            label="Buy Short Signal",
        )

    if buy_long.any():
        plt.plot(
            data.index[buy_long],
            data["Close"][buy_long],
            "^",
            markersize=8,
            color="green",
            label="Buy Long Signal",
        )

    plt.legend()
    plt.grid(True)
    plt.show()


def plot_results(equity_curve, dates):
    """
    Plot the equity curve and drawdown of the back test results.

    Args:
        equity_curve (list): List of equity values over time.
        dates (list): List of dates corresponding to the equity values.
    """
    equity_series = pd.Series(equity_curve, index=dates)
    plot_equity_curve(equity_series)
    plot_drawdown(equity_series)


def plot_trades(price_data, transactions):
    """
    Plots the price data along with buy/sell signals from the transactions.

    Args:
        price_data (pd.DataFrame): DataFrame with 'Close' prices and index as dates.
        transactions (list): List of transaction dictionaries.
    """
    # Create a DataFrame with the buy/sell signals for short and long trades
    # Transactions : [{'action': 'open', 'position_type': 'short', 'price': 66839.532265625, 'amount': 0.0005984482333155352, 'date': Timestamp('2024-10-24 10:06:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'short', 'price': 66953.24100781251, 'amount': 0.0005984482333155352, 'date': Timestamp('2024-10-24 10:28:00+0000', tz='UTC'), 'pnl': -0.06804879587464341}, {'action': 'open', 'position_type': 'short', 'price': 66920.179421875, 'amount': 0.000597767703216271, 'date': Timestamp('2024-10-24 10:30:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'short', 'price': 67001.24043359376, 'amount': 0.000597767703216271, 'date': Timestamp('2024-10-24 10:32:00+0000', tz='UTC'), 'pnl': -0.048455654795510825}, {'action': 'open', 'position_type': 'short', 'price': 67010.98555859375, 'amount': 0.0005969865962208111, 'date': Timestamp('2024-10-24 10:33:00+0000', tz='UTC')}, {'action': 'open', 'position_type': 'long', 'price': 66976.77633984375, 'amount': 0.0005733998539439905, 'date': Timestamp('2024-10-24 10:46:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'long', 'price': 66924.96919921874, 'amount': 0.0005733998539439905, 'date': Timestamp('2024-10-24 10:50:00+0000', tz='UTC'), 'pnl': -0.029706206867636052}, {'action': 'open', 'position_type': 'long', 'price': 66920.724890625, 'amount': 0.000573862366036788, 'date': Timestamp('2024-10-24 10:51:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'short', 'price': 67084.12865625, 'amount': 0.0005969865962208111, 'date': Timestamp('2024-10-24 11:31:00+0000', tz='UTC'), 'pnl': -0.04366544890685413}, {'action': 'open', 'position_type': 'short', 'price': 67051.40283984375, 'amount': 0.0005737253136774606, 'date': Timestamp('2024-10-24 11:32:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'short', 'price': 67087.75184375, 'amount': 0.0005737253136774606, 'date': Timestamp('2024-10-24 11:33:00+0000', tz='UTC'), 'pnl': -0.02085434366797385}, {'action': 'open', 'position_type': 'short', 'price': 67138.53893750001, 'amount': 0.0005729931259952189, 'date': Timestamp('2024-10-24 11:34:00+0000', tz='UTC')}, {'action': 'close', 'position_type': 'short', 'price': 67194.08146484375, 'amount': 0.0005729931259952189, 'date': Timestamp('2024-10-24 11:49:00+0000', tz='UTC'), 'pnl': -0.031825486368366296}, {'action': 'open', 'position_type': 'short', 'price': 67174.74738671875, 'amount': 0.0005727032228127263, 'date': Timestamp('2024-10-24 11:50:00+0000', tz='UTC')}]
    signals = pd.DataFrame(index=price_data.index)

    # BUY SHORT : v red
    # BUY LONG : ^ green
    # SELL SHORT : ^ red
    # SELL LONG : v green

    for trade in transactions:
        if trade["action"] == "open":
            if trade["position_type"] == "short":
                signals.loc[trade["date"], "Short"] = price_data.loc[
                    trade["date"], "Close"
                ]
            elif trade["position_type"] == "long":
                signals.loc[trade["date"], "Long"] = price_data.loc[
                    trade["date"], "Close"
                ]
        elif trade["action"] == "close":
            if trade["position_type"] == "short":
                signals.loc[trade["date"], "Cover"] = price_data.loc[
                    trade["date"], "Close"
                ]
            elif trade["position_type"] == "long":
                signals.loc[trade["date"], "Sell"] = price_data.loc[
                    trade["date"], "Close"
                ]

    # Plot the price data
    plt.figure(figsize=(14, 7))
    plt.plot(price_data.index, price_data["Close"], label="Close Price")

    # Plot the buy/sell signals
    plt.plot(
        signals.index,
        signals["Short"],
        "^",
        markersize=8,
        color="red",
        label="Buy Short Signal",
    )
    plt.plot(
        signals.index,
        signals["Long"],
        "^",
        markersize=8,
        color="green",
        label="Buy Long Signal",
    )
    plt.plot(
        signals.index,
        signals["Cover"],
        "v",
        markersize=8,
        color="red",
        label="Sell Short Signal",
    )
    plt.plot(
        signals.index,
        signals["Sell"],
        "v",
        markersize=8,
        color="green",
        label="Sell Long Signal",
    )

    plt.title("Buy/Sell Signals", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Price", fontsize=14)
    plt.grid(True)
    plt.legend()
    plt.show()
