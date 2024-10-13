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
)
from .strategy import generate_signals
from .data_collector import get_data_for_period
from .executor import TradingExecutor


def collect_and_save_data(
    ticker: str, start_date: str, end_date: str, interval: str = "1d"
):
    """
    Collect stock data for a specified period and save it to CSV.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date (YYYY-MM-DD).
        end_date (str): The end date (YYYY-MM-DD).
        interval (str): The data interval (e.g., '1d', '1h').

    Returns:
        pd.DataFrame: The collected stock data.
    """
    logging.info(f"Collecting data for {ticker} from {start_date} to {end_date}...")
    data = get_data_for_period(
        ticker, start_date, end_date, interval=interval, save_to_csv=True
    )
    logging.info(f"Data for {ticker} collected and saved.")
    return data


def run_back_test(
    ticker,
    start_date,
    end_date,
    initial_cash=10000,
    transaction_cost=0.001,
    leverage=1,
    stop_loss_pct=0.005,
    take_profit_pct=0.005,
    slippage_pct=0.0005,
    interval="1m",
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
        stop_loss_pct (float): Stop-loss percentage.
        take_profit_pct (float): Take-profit percentage.
        slippage_pct (float): Slippage percentage.
        interval (str): Data interval (e.g., '1m' for 1-minute data).

    Returns:
        dict: Back test results.
    """
    print(f"Running back tests for {ticker} from {start_date} to {end_date}...")

    data = get_data_for_period(
        ticker, start_date, end_date, interval=interval, save_to_csv=False
    )
    period = f"{start_date}_{end_date}"
    logging.info(f"Processing data for {ticker} ({period})...")
    processed_data = process_data(
        data,
        ticker,
        period,
        sma_period=5,
        rsi_period=7,
        bbands_period=20,
        atr_period=14,
    )
    signals = generate_signals(processed_data)

    executor = TradingExecutor(
        initial_cash=initial_cash,
        transaction_cost=transaction_cost,
        leverage=leverage,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        slippage_pct=slippage_pct,
    )
    transactions = []

    equity_curve = []
    dates = []

    signals = signals.sort_index()

    for index, row in signals.iterrows():
        signal = row["Signal"]
        price = row["Close"]
        date = index

        # Adjust stop-loss and take-profit dynamically based on ATR
        executor.stop_loss_pct = row["ATR_Stop_Loss"] / price
        executor.take_profit_pct = row["ATR_Take_Profit"] / price

        # Execute the signal
        executor.execute_signal(signal, price, date)

        # Record transactions if new ones have occurred
        if executor.history and (
            not transactions or executor.history[-1] != transactions[-1]
        ):
            last_transaction = executor.history[-1]
            transactions.append(last_transaction)

        # Update equity curve
        total_value = executor.get_total_portfolio_value(price)
        equity_curve.append(total_value)
        dates.append(date)

    final_value = executor.get_total_portfolio_value(price)
    pct_return = calculate_percentage_return(initial_cash, final_value)
    max_drawdown = calculate_max_drawdown(pd.Series(equity_curve))
    sharpe_ratio = calculate_sharpe_ratio(pd.Series(equity_curve).pct_change())
    sortino_ratio = calculate_sortino_ratio(pd.Series(equity_curve).pct_change())

    print(f"Percentage Return: {pct_return:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Sortino Ratio: {sortino_ratio:.2f}")
    print("Transaction History:")
    for txn in transactions:
        action = txn["action"]
        pos_type = txn.get("position_type", "")
        price = txn["price"]
        amount = txn["amount"]
        date = txn["date"]
        pnl = txn.get("profit_loss", "")
        print(f"{date}: {action} {pos_type} {amount} at ${price:.2f} P&L: {pnl}")

    return {
        "executor": executor,
        "transactions": transactions,
        "equity_curve": pd.Series(equity_curve, index=dates),
        "signals": signals,
    }
