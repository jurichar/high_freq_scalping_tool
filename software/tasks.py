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

from tqdm import tqdm
from software.data_collector import get_data_for_period
from software.executor import TradingExecutor


def fetch_data(ticker, start_date, end_date, interval="1d"):
    """
    Fetch historical data for a given stock ticker and date range.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Start date for data collection.
        end_date (str): End date for data collection.
        interval (str): Data interval (e.g., '1d' for daily data).

    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    data = get_data_for_period(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
        save_to_csv=False,
    )

    if data.empty:
        logging.error("No data fetched. Exiting backtest.")
        return pd.DataFrame()

    logging.info(
        f"Data for {ticker} from {start_date} to {end_date} fetched successfully."
    )
    return data


def build_backtest_report(
    transactions,
    equity_curve,
    signals,
    performance_metrics,
    start_date,
    end_date,
    num_frames,
):
    """
    Build a report with backtest results and performance metrics.

    Args:
        transactions (list): List of transaction dictionaries.
        equity_curve (list): List of equity values over time.
        signals (pd.DataFrame): DataFrame of trading signals.
        performance_metrics (dict): Performance metrics of the trading strategy.
        start_date (str): Start date of the backtest.
        end_date (str): End date of the backtest.
        num_frames (int): Number of data frames (rows of data).

    Returns:
        dict: Back test results report.
    """
    num_operations = len(transactions)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "num_frames": num_frames,
        "num_operations": num_operations,
        "transactions": transactions,
        "equity_curve": equity_curve,
        "signals": signals,
        "performance_metrics": performance_metrics,
    }


def execute_trades(
    data, initial_cash, transaction_cost, leverage, slippage_pct, risk_per_trade
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

    print("Executing trades with this : ", data)

    for index, row in tqdm(data.iterrows(), total=len(data), desc="Executing trades"):
        signal = row["Signal"]
        price = row["Close"]
        high_price = row["High"]
        low_price = row["Low"]
        date = index

        executor.execute_signal(signal, price, date, high_price, low_price)

        if executor.history and (
            not transactions or executor.history[-1] != transactions[-1]
        ):
            last_transaction = executor.history[-1]
            transactions.append(last_transaction)

        total_value = executor.get_total_portfolio_value(price)
        equity_curve.append(total_value)
        dates.append(date)

    return transactions, equity_curve, dates
