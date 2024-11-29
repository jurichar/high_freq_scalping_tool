'''
File: strategy_sell.py
Project: software
File Created: Monday, 4th November 2024 2:11:48 am
Author: Julien RICHARD (jurichar@student.42.fr)
-----
Last Modified: Friday, 29th November 2024 1:30:03 am
Modified By: Julien RICHARD (jurichar@student.42.fr>)
-----
Copyright 2017 - 2024 jurichar
'''

import pandas as pd
from software.position import Position


def update_trailing_stop(
    position: Position, price: float, stop_loss_price: float
):
    """
    Update the trailing stop-loss for a given position based on the current price and ATR.

    Args:
        position (Position): The position to update.
        price (float): Current price of the asset.
        stop_loss_price (float): ATR-based stop-loss adjustment factor.

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
        if stop_loss_price > position.stop_loss_price:
                position.stop_loss_price = stop_loss_price
    elif position.type == "short":
        if stop_loss_price < position.stop_loss_price:
            position.stop_loss_price = stop_loss_price


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
