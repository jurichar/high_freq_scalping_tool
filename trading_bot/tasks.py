"""
tasks.py

Module for orchestrating the key operations of the trading bot, such as data collection, 
processing, and backtesting.

Functions:
- collect_and_save_data: Collects data for a specific period and saves it.
- process_data: Cleans data and adds technical indicators.
- run_backtest: Runs a backtest using historical data and displays performance metrics.
"""

import logging
import pandas as pd
from trading_bot.data_collector import get_data_for_period
from trading_bot.utils import (
    calculate_max_drawdown,
    calculate_percentage_return,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
)
from .data_processor import (
    clean_data,
    add_technical_indicators,
    normalize_data,
    save_processed_data,
)
from .strategy import generate_signals
from .executor import TradingExecutor
from datetime import datetime


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


def process_data(ticker: str, data: pd.DataFrame, period: str = "1y"):
    """
    Process stock data by cleaning and adding technical indicators, then save it.

    Args:
        ticker (str): The stock ticker symbol.
        data (pd.DataFrame): The stock data to process.
        period (str): The period of the data.

    Returns:
        pd.DataFrame: The processed stock data with technical indicators.
    """
    logging.info(f"Processing data for {ticker}...")
    data = clean_data(data)
    data = add_technical_indicators(data)
    data = normalize_data(data)
    save_processed_data(data, ticker, period)
    logging.info(f"Data for {ticker} processed and saved.")
    return data


def run_backtest(
    ticker: str,
    start_date: str,
    end_date: str,
    compare_start: str,
    compare_end: str,
    initial_cash: float = 10000,
    transaction_cost: float = 0.001,
    interval: str = "1d",
):
    """
    Run a backtest by comparing the signals generated by the strategy with actual stock data.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): The start date for the training period.
        end_date (str): The end date for the training period.
        compare_start (str): The start date for the comparison period.
        compare_end (str): The end date for the comparison period.
        initial_cash (float): The initial cash for the trading simulation.

    Returns:
        None
    """
    compare_start = pd.Timestamp(compare_start).tz_localize("America/New_York")
    compare_end = pd.Timestamp(compare_end).tz_localize("America/New_York")
    final_end_date = max(
        compare_end, pd.Timestamp(end_date).tz_localize("America/New_York")
    )

    print(f"Running backtest for {ticker} from {start_date} to {compare_end}...")

    data = collect_and_save_data(ticker, start_date, final_end_date, interval)
    processed_data = process_data(ticker, data)
    signals = generate_signals(processed_data)
    executor = TradingExecutor(
        initial_cash=initial_cash, transaction_cost=transaction_cost
    )
    transactions = []

    def record_transaction(action, price, amount, date):
        transactions.append(
            {"action": action, "price": price, "amount": amount, "date": date}
        )

    equity_curve = []
    for index, row in signals.iterrows():
        if compare_start <= index <= compare_end:
            signal = row["Filtered_Signal"]
            action = "buy" if signal == 1 else "sell" if signal == -1 else "hold"
            if action in ["buy", "sell"]:
                executor.execute_orders(pd.DataFrame([row]))
                record_transaction(action, row["Close"], 1, index)
            total_value = executor.cash + executor.stock_balance * row["Close"]
            equity_curve.append(total_value)

    final_value = (
        executor.cash + executor.stock_balance * signals.loc[compare_end]["Close"]
    )
    pct_return = calculate_percentage_return(initial_cash, final_value)
    max_drawdown = calculate_max_drawdown(pd.Series(equity_curve))
    sharpe_ratio = calculate_sharpe_ratio(pd.Series(equity_curve).pct_change())
    sortino_ratio = calculate_sortino_ratio(pd.Series(equity_curve).pct_change())

    print(f"Percentage Return: {pct_return}%")
    print(f"Max Drawdown: {max_drawdown}%")
    print(f"Sharpe Ratio: {sharpe_ratio}")
    print(f"Sortino Ratio: {sortino_ratio}")
    print("Transaction History:", transactions)

    return {
        "executor": executor,
        "transactions": transactions,
        "equity_curve": equity_curve,
        "signals": signals,
    }


# Example usage
if __name__ == "__main__":
    import doctest

    doctest.testmod()

    run_backtest(
        ticker="MSFT",
        start_date="2020-01-01",
        end_date="2020-03-31",
        compare_start="2020-04-01",
        compare_end="2020-06-30",
    )
