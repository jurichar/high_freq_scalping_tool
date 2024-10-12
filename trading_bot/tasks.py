"""
tasks.py

Module for orchestrating the key operations of the trading bot, such as data collection, 
processing, and backtesting.

Functions:
- collect_and_save_data: Collects data for a specific period and saves it.
- run_backtest: Runs a backtest using historical data and displays performance metrics.
"""

import logging
import pandas as pd
from trading_bot.data_collector import get_data_for_period
from trading_bot.data_processor import process_data
from trading_bot.utils import (
    calculate_max_drawdown,
    calculate_percentage_return,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
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


import logging
import pandas as pd
from .data_collector import get_data_for_period
from .data_processor import (
    clean_data,
    add_technical_indicators,
    normalize_data,
    save_processed_data,
)
from .strategy import generate_signals
from .executor import TradingExecutor
from .utils import (
    calculate_max_drawdown,
    calculate_percentage_return,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
)


def run_backtest(
    ticker,
    start_date,
    end_date,
    compare_start,
    compare_end,
    initial_cash=10000,
    transaction_cost=0.001,
    leverage=1,
    stop_loss=0.05,
    take_profit=0.1,
    interval="1d",
):
    """
    Run a backtest, adding new stop-loss, take-profit, and dynamic leverage.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Start date for training.
        end_date (str): End date for training.
        compare_start (str): Start date for comparison.
        compare_end (str): End date for comparison.
        initial_cash (float): Initial cash for the simulation.
        leverage (float): Leverage factor.
        stop_loss (float): Stop-loss percentage.
        take_profit (float): Take-profit percentage.

    Returns:
        dict: Backtest results.
    """
    compare_start = pd.Timestamp(compare_start).tz_localize("America/New_York")
    compare_end = pd.Timestamp(compare_end).tz_localize("America/New_York")

    print(f"Running backtest for {ticker} from {start_date} to {compare_end}...")

    data = get_data_for_period(
        ticker, start_date, compare_end, interval=interval, save_to_csv=True
    )
    period = f"{start_date}_{compare_end}"
    print(f"Processing data for {ticker} ({period})...")
    processed_data = process_data(
        data,
        ticker,
        period,
        sma_period=5,
        rsi_period=14,
        bbands_period=20,
        atr_period=14,
    )
    signals = generate_signals(processed_data)

    executor = TradingExecutor(
        initial_cash=initial_cash,
        transaction_cost=transaction_cost,
        leverage=leverage,
        stop_loss=stop_loss,
        take_profit=take_profit,
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

    if compare_end not in signals.index:
        logging.warning(
            f"Timestamp {compare_end} not found, using the last available timestamp during trading hours."
        )
        compare_end = signals.index[-1]

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
