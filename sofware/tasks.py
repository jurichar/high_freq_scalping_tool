"""
tasks.py

Module for orchestrating the key operations of the trading bot, such as data collection,
processing, and back testing.

Functions:
- collect_and_save_data: Collects data for a specific period and saves it.
- run_back test: Runs a back test using historical data and displays performance metrics.
"""

import logging
import pandas as pd
from datetime import datetime
from sofware.data_processor import process_data
from sofware.analysis import (
    calculate_max_drawdown,
    calculate_percentage_return,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
    calculate_win_loss_ratio,
    calculate_profit_factor,
)
from .strategy import generate_signals
from .data_collector import get_data_for_period
from .executor import TradingExecutor
import matplotlib.pyplot as plt


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


def fetch_data(ticker, start_date, end_date, interval="1d"):
    data = get_data_for_period(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
        save_to_csv=False,
    )

    if data.empty:
        logging.error("No data fetched. Exiting backtest.")
        return {}

    period = f"{start_date}_{end_date}"
    logging.info(f"Processing data for {ticker} ({period})...")
    return data


def run_back_test(
    ticker,
    start_date,
    end_date,
    initial_cash=10000,
    transaction_cost=0.001,
    leverage=1,
    slippage_pct=0.0005,
    risk_per_trade=0.01,
    interval="1m",
    sma_period=5,
    rsi_period=7,
    bbands_period=20,
    atr_period=14,
):
    """
    Run a back test using high-frequency data and display performance metrics.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Start date for data collection.
        end_date (str): End date for data collection.
        initial_cash (float): Initial cash for the simulation.
        transaction_cost (float): Transaction cost.
        leverage (float): Leverage factor.
        slippage_pct (float): Slippage percentage.
        risk_per_trade (float): Fraction of portfolio to risk per trade.
        interval (str): Data interval (e.g., '1m' for 1-minute data).
        sma_period (int): Period for the Simple Moving Average (SMA) indicator.
        rsi_period (int): Period for the Relative Strength Index (RSI) indicator.
        bbands_period (int): Period for the Bollinger Bands indicator.
        atr_period (int): Period for the Average True Range (ATR) indicator.

    Returns:
        dict: Back test results including additional metrics.
    """
    print(f"Running back tests for {ticker} from {start_date} to {end_date}...")

    data = fetch_data(ticker, start_date, end_date, interval)

    if not isinstance(data, pd.DataFrame) or data.empty:
        logging.error(
            "Data is not a valid pandas DataFrame or is empty. Exiting backtest."
        )
        return {}

    processed_data = process_data(
        data,
        ticker,
        sma_period=sma_period,
        rsi_period=rsi_period,
        bbands_period=bbands_period,
        atr_period=atr_period,
    )

    # Generate signals
    signals = generate_signals(processed_data)

    if signals.empty:
        logging.warning("No signals generated. Exiting backtest.")
        return {}

    transactions, equity_curve, dates = execute_trades(
        signals,
        initial_cash,
        transaction_cost,
        leverage,
        slippage_pct,
        risk_per_trade,
    )

    performance_metrics = evaluate_performance(transactions, equity_curve, initial_cash)

    if equity_curve:
        equity_series = pd.Series(equity_curve, index=dates)
        plot_equity_curve(equity_series)
        plot_drawdown(equity_series)
    else:
        logging.warning("Equity curve is empty. No plots to display.")

    return {
        "transactions": transactions,
        "equity_curve": pd.Series(equity_curve, index=dates),
        "signals": signals,
        "performance_metrics": performance_metrics,
    }


def execute_trades(
    signals, initial_cash, transaction_cost, leverage, slippage_pct, risk_per_trade
):
    executor = TradingExecutor(
        initial_cash=initial_cash,
        transaction_cost=transaction_cost,
        leverage=leverage,
        slippage_pct=slippage_pct,
        risk_per_trade=risk_per_trade,
    )

    transactions = []
    equity_curve = []
    dates = []
    signals = signals.sort_index()

    # Execute trades based on signals
    for index, row in signals.iterrows():
        signal = row["Signal"]
        price = row["Close"]
        high_price = row["High"]
        low_price = row["Low"]
        date = index

        atr_stop_loss = row["ATR_Stop_Loss"]
        atr_take_profit = row["ATR_Take_Profit"]

        executor.execute_signal(
            signal, price, date, high_price, low_price, atr_stop_loss, atr_take_profit
        )

        if executor.history and (
            not transactions or executor.history[-1] != transactions[-1]
        ):
            last_transaction = executor.history[-1]
            transactions.append(last_transaction)

        total_value = executor.get_total_portfolio_value(price)
        equity_curve.append(total_value)
        dates.append(date)

    return transactions, equity_curve, dates


def evaluate_performance(transactions, equity_curve, initial_cash):
    """
    Evaluate the performance of the trading strategy.

    Args:
        transactions (list): List of transaction dictionaries.
        equity_curve (list): List of equity values over time.
        initial_cash (float): Initial cash value.

    Returns:
        dict: Performance metrics of the trading strategy.
    """
    final_value = equity_curve[-1]
    pct_return = calculate_percentage_return(initial_cash, final_value)
    max_drawdown = calculate_max_drawdown(pd.Series(equity_curve))
    sharpe_ratio = calculate_sharpe_ratio(pd.Series(equity_curve).pct_change())
    sortino_ratio = calculate_sortino_ratio(pd.Series(equity_curve).pct_change())
    calmar_ratio = calculate_calmar_ratio(pct_return, max_drawdown)
    win_loss_ratio = calculate_win_loss_ratio(transactions)
    profit_factor = calculate_profit_factor(transactions)

    return {
        "Percentage Return": pct_return,
        "Max Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Calmar Ratio": calmar_ratio,
        "Win/Loss Ratio": win_loss_ratio,
        "Profit Factor": profit_factor,
    }
