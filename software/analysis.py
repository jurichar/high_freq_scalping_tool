"""
analysis.py

Module for calculating performance metrics of a trading strategy.
"""

import pandas as pd
import numpy as np


def calculate_percentage_return(initial_cash, final_value):
    """
    Args:
        initial_cash (float): The initial cash value.
        final_value (float): The final value of the portfolio.
    Returns:
        float: Percentage return on investment.

    Example:
    >>> calculate_percentage_return(1000, 1200)
    20.0
    """
    return ((final_value - initial_cash) / initial_cash) * 100


def calculate_max_drawdown(equity_curve):
    """
    Args:
        equity_curve (pd.Series): The equity curve of the portfolio over time.
    Returns:
        float: Maximum drawdown percentage.

    Example:
    >>> equity_curve = pd.Series([100, 110, 90, 120, 80])
    >>> calculate_max_drawdown(equity_curve)
    -33.33333333333333
    """
    roll_max = equity_curve.cummax()
    drawdown = (equity_curve - roll_max) / roll_max
    return drawdown.min() * 100


def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """
    Args:
        returns (pd.Series): The daily or weekly returns of the strategy.
        risk_free_rate (float): The risk-free rate, e.g., return on Treasury bills.
    Returns:
        float: The Sharpe ratio.

    Example:
    >>> returns = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015])
    >>> calculate_sharpe_ratio(returns)
    0.6949955884209108
    """
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(returns, risk_free_rate=0):
    """
    Calculates the Sortino ratio of a return series.

    Args:
        returns (pd.Series): The daily or weekly returns of the strategy.
        risk_free_rate (float): The risk-free rate.
    Returns:
        float: The Sortino ratio.

    Example:
    >>> returns = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015])
    >>> round(calculate_sortino_ratio(returns), 6)
    0.8
    """
    expected_return = returns.mean() - risk_free_rate
    downside_returns = returns[returns < risk_free_rate]
    if len(downside_returns) == 0:
        return np.nan
    downside_deviation = np.sqrt(np.mean((downside_returns - risk_free_rate) ** 2))
    if downside_deviation == 0 or np.isnan(downside_deviation):
        return np.nan
    return expected_return / downside_deviation


def calculate_calmar_ratio(percentage_return, max_drawdown):
    """
    Calculate the Calmar Ratio.

    Args:
        percentage_return (float): The percentage return of the strategy.
        max_drawdown (float): The maximum drawdown percentage.

    Returns:
        float: Calmar Ratio.
    """
    if max_drawdown == 0:
        return np.nan
    return percentage_return / abs(max_drawdown)


def calculate_win_loss_ratio(transactions):
    """
    Calculate the Win/Loss Ratio.

    Args:
        transactions (list): List of transaction dictionaries.

    Returns:
        float: Win/Loss Ratio.
    """
    wins = sum(1 for txn in transactions if txn.get("profit_loss", 0) > 0)
    losses = sum(1 for txn in transactions if txn.get("profit_loss", 0) < 0)
    if losses == 0:
        return np.nan
    return wins / losses


def calculate_profit_factor(transactions):
    """
    Calculate the Profit Factor.

    Args:
        transactions (list): List of transaction dictionaries.

    Returns:
        float: Profit Factor.
    """
    gross_profit = sum(
        txn["profit_loss"] for txn in transactions if txn.get("profit_loss", 0) > 0
    )
    gross_loss = -sum(
        txn["profit_loss"] for txn in transactions if txn.get("profit_loss", 0) < 0
    )
    if gross_loss == 0:
        return np.nan
    return gross_profit / gross_loss


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
