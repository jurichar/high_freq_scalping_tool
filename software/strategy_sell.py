# strategy_sell.py

import pandas as pd
from software.position import Position


def update_trailing_stop(
    position: Position, price: float, atr_stop_loss: float
):
    """
    Update the trailing stop-loss for a given position based on the current price and ATR.

    Args:
        position (Position): The position to update.
        price (float): Current price of the asset.
        atr_stop_loss (float): ATR-based stop-loss adjustment factor.

    Examples:
        >>> position = Position("long", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 90
        >>> update_trailing_stop(position, 110, 5)
        >>> position.stop_loss_price
        100

        >>> position = Position("short", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 110
        >>> update_trailing_stop(position, 90, 5)
        >>> position.stop_loss_price
        100

        >>> position = Position("long", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 90
        >>> update_trailing_stop(position, 90, 5)
        >>> position.stop_loss_price
        90

        >>> position = Position("short", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 110
        >>> update_trailing_stop(position, 110, 5)
        >>> position.stop_loss_price
        110
    """
    if position.type == "long":
        new_stop_loss = price - 2 * atr_stop_loss
        if new_stop_loss > position.stop_loss_price:
                position.stop_loss_price = new_stop_loss
    elif position.type == "short":
        new_stop_loss = price + 2 * atr_stop_loss
        if new_stop_loss < position.stop_loss_price:
            position.stop_loss_price = new_stop_loss


def check_stop_loss(position: Position, price: float) -> bool:
    """
    Check if the stop-loss has been hit for the given position.

    Args:
        position (Position): The position to check.
        price (float): Current price of the asset.

    Returns:
        bool: True if stop-loss is hit, False otherwise.

        Position :
        position_type: str,
        amount: float,
        entry_price: float,
        entry_date: pd.Timestamp,
    Examples:
        >>> position = Position("long", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 90
        >>> check_stop_loss(position, 80)
        True

        >>> position = Position("short", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 110
        >>> check_stop_loss(position, 120)
        True

        >>> position = Position("long", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 90
        >>> check_stop_loss(position, 100)
        False

        >>> position = Position("short", 1, 100, pd.Timestamp("2024-01-01"))
        >>> position.stop_loss_price = 110
        >>> check_stop_loss(position, 100)
        False
    """
    if position.type == "long" and price <= position.stop_loss_price:
        return True
    elif position.type == "short" and price >= position.stop_loss_price:
        return True
    return False
