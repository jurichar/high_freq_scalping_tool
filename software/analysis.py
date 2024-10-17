"""
analysis.py

Module for calculating performance metrics of a trading strategy.
"""

import pandas as pd
import numpy as np
import logging


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


def calculate_exit_prices(
    position_type, price, stop_loss_pct, take_profit_pct, slippage_pct
):
    """
    Calculate the stop-loss, take-profit, and adjusted prices based on the position type.
    The stop-loss and take-profit prices are calculated as a percentage of the current price.
    The adjusted price accounts for slippage.

    Args:
        position_type (str): Type of position ("long" or "short").
        price (float): Current price of the asset.
        stop_loss_pct (float): Stop-loss percentage.
        take_profit_pct (float): Take-profit percentage.
        slippage_pct (float): Slippage percentage.

    Returns:
        tuple: (stop_loss, take_profit, adjusted_price)

    Examples:
        >>> calculate_exit_prices(position_type="long", price=100, stop_loss_pct=0.02, take_profit_pct=0.04, slippage_pct=0.01)
        (98.0, 104.0, 101.0)
        >>> calculate_exit_prices(position_type="short", price=100, stop_loss_pct=0.02, take_profit_pct=0.04, slippage_pct=0.01)
        (102.0, 96.0, 99.0)
    """

    if position_type == "long":
        stop_loss = price * (1 - stop_loss_pct)
        take_profit = price * (1 + take_profit_pct)
        adjusted_price = price * (1 + slippage_pct)
    elif position_type == "short":
        stop_loss = price * (1 + stop_loss_pct)
        take_profit = price * (1 - take_profit_pct)
        adjusted_price = price * (1 - slippage_pct)
    else:
        raise ValueError(f"Unknown position type: {position_type}")
    return stop_loss, take_profit, adjusted_price


def calculate_size(price, equity, stop_loss_pct, risk_per_trade):
    """
    Calculate the position size based on the risk per trade and stop-loss percentage.
    The position size is the number of units of an asset to buy or sell.

    Args:
        price (float): Current price of the asset.
        equity (float): Total equity available for trading.
        stop_loss_pct (float): Stop-loss percentage.
        risk_per_trade (float): Maximum risk per trade as a percentage of equity.

    Returns:
        float: Position size.

    Examples:
        >>> calculate_size(price=100, equity=10000, stop_loss_pct=0.02, risk_per_trade=0.01)
        50.0
    """
    atr_stop_loss_dollar = stop_loss_pct * price
    risk_amount = equity * risk_per_trade

    if atr_stop_loss_dollar > risk_amount:
        logging.warning(
            "Stop-loss dollar value exceeds risk amount. Reducing position size."
        )
        return equity / price

    return risk_amount / atr_stop_loss_dollar


def apply_slippage(price, position_type, slippage_pct):
    """
    Apply slippage to the price based on the position type.
    Slippage is positive for long positions and negative for short positions.
    Slippage is a percentage of the price that represents the cost of executing the trade.

    Args:
        price (float): Current price of the asset.
        position_type (str): Type of position ("long" or "short").
        slippage_pct (float): Slippage percentage.

    Returns:
        float: Adjusted price after slippage.

    Examples:
        >>> apply_slippage(price=100, position_type="long", slippage_pct=0.01)
        99.0
        >>> apply_slippage(price=100, position_type="short", slippage_pct=0.01)
        101.0
    """
    return (
        price * (1 - slippage_pct)
        if position_type == "long"
        else price * (1 + slippage_pct)
    )


def calculate_proceeds(adjusted_price, amount, transaction_cost):
    """
    Calculate the proceeds from selling an asset.
    The proceeds are the total value received after accounting for transaction costs.

    Args:
        adjusted_price (float): Adjusted price of the asset after slippage.
        amount (float): Number of units of the asset.
        transaction_cost (float): Transaction cost as a percentage of the total value.

    Returns:
        float: Total proceeds from the sale.

    Examples:
        >>> calculate_proceeds(amount=100, adjusted_price=100, transaction_cost=0.01)
        999.0
    """

    return adjusted_price * amount * (1 - transaction_cost)
