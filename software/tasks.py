'''
File: tasks.py
Project: software
File Created: Monday, 7th October 2024 5:36:05 pm
Author: Julien RICHARD (jurichar@student.42.fr)
-----
Last Modified: Friday, 29th November 2024 1:29:57 am
Modified By: Julien RICHARD (jurichar@student.42.fr>)
-----
Copyright 2017 - 2024 jurichar
'''

import logging
import pandas as pd

from tqdm import tqdm
from software.data_collector import get_data_for_period
from software.executor import TradingExecutor


def fetch_clean_data(ticker, start_date, end_date, interval="1d"):
    """
    Fetch historical data for a given stock ticker and date range.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Start date for data collection.
        end_date (str): End date for data collection.
        interval (str): Data interval (e.g., '1d' for daily data).

    Returns:
        pd.DataFrame: DataFrame with historical stock data.

    Example:
        >>> df = fetch_clean_data("AAPL", "2021-01-01", "2021-12-31")
        >>> df.shape[1]
        7
        >>> 'Open' in df.columns
        True
        >>> df.empty
        False

        >>> df = fetch_clean_data("AAPL", "2021-01-01", "2021-01-01")
        >>> df.empty
        True

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
        f"Data for {ticker} from {start_date} to {end_date}\
            fetched successfully."
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
        performance_metrics (dict): Performance metrics
            of the trading strategy.
        start_date (str): Start date of the backtest.
        end_date (str): End date of the backtest.
        num_frames (int): Number of data frames (rows of data).

    Returns:
        dict: Back test results report.

    Example:
        >>> transactions = [
        ...     {"date": "2021-01-01", "type": "buy", "price": 100},
        ...     {"date": "2021-01-02", "type": "sell", "price": 110},
        ... ]
        >>> equity_curve = [100, 110]
        >>> signals = pd.DataFrame({"Signal": [1, -1]})
        >>> performance_metrics = {"total_return": 0.1}
        >>> start_date = "2021-01-01"
        >>> end_date = "2021-01-02"
        >>> num_frames = 2
        >>> report = build_backtest_report(
        ...     transactions, equity_curve, signals, performance_metrics,
        ...     start_date, end_date, num_frames
        ... )
        >>> report["num_operations"]
        2
        >>> report["end_date"]
        '2021-01-02'
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
    data: pd.DataFrame,
    initial_cash: float,
    transaction_cost: float,
    leverage: float,
    slippage_pct: float,
    risk_per_trade: float,
):
    """
    Execute trades based on the trading signals and data.

    Args:
        data (pd.DataFrame): DataFrame with historical stock data.
        initial_cash (float): Initial capital for trading.
        transaction_cost (float): Cost per transaction.
        leverage (float): Leverage used in trading.
        slippage_pct (float): Slippage percentage.
        risk_per_trade (float): Maximum risk per trade as a percentage.

    Returns:
        tuple: A tuple containing the transactions, equity curve, and dates.

    Example:
        >>> data = pd.DataFrame({
        ...     "Close": [100, 101, 102],
        ...     "Signal": [1, -1, 0],
        ...     "ATR": [2, 2.1, 2.2]
        ... })
        >>> transactions, equity_curve, dates = execute_trades(
        ...     data, initial_cash=1000, transaction_cost=0.01,
        ...     leverage=2, slippage_pct=0.01, risk_per_trade=0.02
        ... )
        >>> len(transactions)
        1
        >>> len(equity_curve)
        3
        >>> len(dates)
        3
    """

    transactions = []
    equity_curve = []
    dates = []

    executor = TradingExecutor(
        initial_cash=initial_cash,
        transaction_cost=transaction_cost,
        leverage=leverage,
        slippage_pct=slippage_pct,
        risk_per_trade=risk_per_trade,
    )

    for index, row in tqdm(
        data.iterrows(),
        total=len(data),
        desc="Executing trades",
    ):
        signal = row["Signal"]
        price = row["Close"]
        atr_stop_loss = row["ATR"] * 2
        date = index

        executor.execute_signal(
            signal,
            price,
            atr_stop_loss,
            date,
        )

        executor.update_positions(
            price,
            date,
            atr_stop_loss,
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
