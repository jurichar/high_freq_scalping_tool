"""
backtester.py
"""

from software.data_processor import process_data

# from software.tasks import execute_trades
from software.tasks import fetch_data
from software.utils import validate_data
from software.strategy import Strategy


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
    # num_frames = len(data)

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
        strategy = Strategy(
            ema_sma_threshold=0,
            rsi_long_threshold=30,
            rsi_short_threshold=70,
            bb_threshold=0,
        )
        data_with_signals = strategy.generate_signals(processed_data)

        print("Executing trades...: ", data_with_signals)

        # print("Executing trades...")
        # transactions, equity_curve, dates = execute_trades(
        #     data=data_with_signals,
        #     initial_cash=initial_cash,
        #     transaction_cost=transaction_cost,
        #     leverage=leverage,
        #     slippage_pct=slippage_pct,
        #     risk_per_trade=risk_per_trade,
        # )

        print("Evaluating performance...")
        # performance_metrics = evaluate_performance(
        #     transactions, equity_curve, initial_cash
        # )
        # plot_results(equity_curve, dates)

        # print("Building backtest report...")
        # report = build_backtest_report(
        #     transactions,
        #     equity_curve,
        #     data_with_signals,
        #     performance_metrics,
        #     start_date,
        #     end_date,
        #     num_frames,
        # )
        print("Backtest completed successfully.")
        # print(report)
        # return report
    return None
