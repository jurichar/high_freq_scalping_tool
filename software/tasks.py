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
from software.data_processor import process_data
from software.analysis import evaluate_performance
from tqdm import tqdm
from software.plot_draws import plot_drawdown, plot_equity_curve
from software.utils import validate_data
from .strategy import generate_signals
from .data_collector import get_data_for_period
from .executor import TradingExecutor


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
    ema_period=20,
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

    # Step 1: Fetch data with progress bar for loading market data
    print("Preparing market data for backtest...")
    data = fetch_data(ticker, start_date, end_date, interval)
    num_frames = len(data)

    if validate_data(data):
        processed_data = process_data(
            data=data,
            ticker=ticker,
            sma_period=sma_period,
            ema_period=ema_period,
            rsi_period=rsi_period,
            bbands_period=bbands_period,
            atr_period=atr_period,
        )

        print("Running backtest...")
        signals = generate_signals(processed_data)
        transactions, equity_curve, dates = execute_trades(
            signals,
            initial_cash,
            transaction_cost,
            leverage,
            slippage_pct,
            risk_per_trade,
        )
        performance_metrics = evaluate_performance(
            transactions, equity_curve, initial_cash
        )
        # plot_results(equity_curve, dates)

        report = build_backtest_report(
            transactions,
            equity_curve,
            signals,
            performance_metrics,
            start_date,
            end_date,
            num_frames,
        )
        print("Backtest completed successfully.")
        print(report)
        return report
    return None


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

    for index, row in tqdm(
        signals.iterrows(), total=len(signals), desc="Executing trades"
    ):
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
