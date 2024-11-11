"""
trade_utils.py
"""
import logging

def calculate_size_in_usd(
    account_size: float,
    risk_per_trade: float,
    adjusted_price: float,
    stop_loss_price: float,
):
    """
    Position size is the portion of your total account value that is
    used in any open trade. Depending on the risk per trade.
    The position size is calculated by multiplying your equity by
    the risk per trade and dividing it by the price difference between
    the entry price and the stop-loss price.

    Args:
        account_size (float): Total capital available for trading (in USD).
        risk_per_trade_pct (float): Maximum risk per trade as a percentage
            of account_size (e.g., 0.02 for 2%).
        adjusted_price (float): Entry price of the asset
            (adjusted for slippage).
        stop_loss_price (float): Stop-loss price.

    Returns:
        float: Position size in USD.

    Example:
        >>> calculate_size_in_usd(
        ...     account_size=1000,
        ...     risk_per_trade=0.02,
        ...     adjusted_price=70000,
        ...     stop_loss_price=69000,
        ... )
        1400.0

        >>> calculate_size_in_usd(
        ...     account_size=3000,
        ...     risk_per_trade=0.02,
        ...     adjusted_price=8611.5,
        ...     stop_loss_price=9156.5,
        ... )
        948.06

        >>> calculate_size_in_usd(
        ...     account_size=2000,
        ...     risk_per_trade=0.02,
        ...     adjusted_price=8607.5,
        ...     stop_loss_price=7847.5,
        ... )
        453.03

        >>> calculate_size_in_usd(
        ...     account_size=3000,
        ...     risk_per_trade=0.02,
        ...     adjusted_price=69483.06921093751,
        ...     stop_loss_price=69533.46983426629,
        ... )
        

    """
    account_risk = account_size * risk_per_trade
    sl_size = abs(adjusted_price - stop_loss_price)
    invalidation_point = sl_size / adjusted_price
    position_size = account_risk / invalidation_point
    return round(position_size, 2)


def apply_slippage(price, position_type, slippage_pct):
    """
    Apply slippage to the price based on the position type.
    Slippage is positive for long positions and negative for short positions.
    Slippage is a percentage of the price that represents the cost
    of executing the trade.

    Args:
        price (float): Current price of the asset.
        position_type (str): Type of position ("long" or "short").
        slippage_pct (float): Slippage percentage.

    Returns:
        float: Adjusted price after slippage.

    Examples:
        >>> apply_slippage(price=100, position_type="long", slippage_pct=0.05)
        105.0
        >>> apply_slippage(price=100, position_type="short", slippage_pct=0.05)
        95.0
        >>> apply_slippage(
        ...     price=100,
        ...     position_type="invalid",
        ...     slippage_pct=0.05
        ... )
        Traceback (most recent call last):
        ...
        ValueError: Position type must be 'long' or 'short'.
    """
    if position_type == "long":
        return price * (1 + slippage_pct)
    if position_type == "short":
        return price * (1 - slippage_pct)
    raise ValueError("Position type must be 'long' or 'short'.")


def calculate_exit_prices(
    position_type, price, stop_loss_pct, take_profit_pct, slippage_pct
):
    """
    Calculate the stop-loss, take-profit, and adjusted
    prices based on the position type.
    The stop-loss and take-profit prices are calculated
    as a percentage of the current price.
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
        >>> calculate_exit_prices(
        ...     position_type="long",
        ...     price=100,
        ...     stop_loss_pct=0.02,
        ...     take_profit_pct=0.04,
        ...     slippage_pct=0.01
        ... )
        (98.0, 104.0, 101.0)
        >>> calculate_exit_prices(
        ...     position_type="short",
        ...     price=100,
        ...     stop_loss_pct=0.02,
        ...     take_profit_pct=0.04,
        ...     slippage_pct=0.01
        ... )
        (102.0, 96.0, 99.0)

        >>> calculate_exit_prices(
        ...     position_type="invalid",
        ...     price=100, stop_loss_pct=0.02,
        ...     take_profit_pct=0.04,
        ...     slippage_pct=0.01
        ... )
        Traceback (most recent call last):
        ...
        ValueError: Unknown position type: invalid
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


def calculate_proceeds(adjusted_price,  transaction_cost):
    """
    Calculate the proceeds from selling an asset.
    The proceeds are the total value received after
    accounting for transaction costs.

    Args:
        adjusted_price (float): Adjusted price of the asset after slippage.
        amount (float): Number of units of the asset.
        transaction_cost (float): Transaction cost as a percentage
            of the total value.

    Returns:
        float: Total proceeds from the sale.

    Examples:
        >>> calculate_proceeds(
        ...     amount=100,
        ...     adjusted_price=100,
        ...     transaction_cost=0.01
        ... )
        9900.0
    """
    total_value = adjusted_price
    total_cost = total_value * transaction_cost
    proceeds = total_value - total_cost
    return proceeds
