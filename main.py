"""
main.py

Main script to run the trading bot in real-time.

This script coordinates the data collection, strategy application,
and order execution without using predictive models for now.
"""

import time
import logging
import yfinance as yf
from datetime import datetime, timedelta
from sofware.strategy import generate_signals
from sofware.executor import TradingExecutor

SYMBOL = "MSFT"
SHORT_WINDOW = 50
LONG_WINDOW = 200
INITIAL_CASH = 10000
REFRESH_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def collect_real_time_data(symbol: str, interval: str = "1m", days: int = 7):
    """
    Collect real-time stock data from Yahoo Finance with error handling.

    Args:
        symbol (str): The stock symbol.
        interval (str): The interval for the data (e.g., "1m", "5m").
        days (int): The number of past days to include in the data.

    Returns:
        pd.DataFrame: DataFrame with stock data.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        if data.empty:
            raise ValueError("No data fetched for the given interval and date range.")
        return data
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        logging.info("Trying with a larger interval (e.g., '5m').")
        return yf.download(symbol, start=start_date, end=end_date, interval="5m")


def main():
    executor = TradingExecutor(initial_cash=INITIAL_CASH)

    while True:
        try:
            logging.info("Collecting real-time data...")
            data = collect_real_time_data(SYMBOL, interval="1m", days=7)
            logging.info(f"Data collected for {SYMBOL}.")

            logging.info("Generating trading signals...")
            signals = generate_signals(
                data, short_window=SHORT_WINDOW, long_window=LONG_WINDOW
            )
            logging.info("Signals generated.")

            logging.info("Executing trading orders...")
            executor.execute_orders(signals)

            latest_price = data["Close"].iloc[-1]
            executor.display_portfolio(latest_price)

            logging.info("Recent trading history:")
            for entry in executor.history[-5:]:
                logging.info(entry)

            logging.info(f"Waiting {REFRESH_INTERVAL} seconds before next update...")
            time.sleep(REFRESH_INTERVAL)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    main()
