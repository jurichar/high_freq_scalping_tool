"""
utils.py

Module containing utility functions for the software.
"""

import logging

import pandas as pd


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


def validate_data(data):
    """
    Validate the input data for analysis.

    Args:
        data (pd.DataFrame): Dataframe containing the historical prices.

    Returns:
        bool: True if the data is valid, False otherwise.
    """

    if not isinstance(data, pd.DataFrame) or data.empty:
        logging.error("Invalid or empty data.")
        return False
    return True
