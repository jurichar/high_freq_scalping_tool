"""
position.py
"""

import pandas as pd


class Position:
    """
    Represents an individual position (long or short) in a financial asset.
    """

    def __init__(
        self,
        position_type: str,
        amount: float,
        entry_price: float,
        entry_date: pd.Timestamp,
    ):
        """
        Initializes a position.

        Args:
            position_type (str): Type of position ('long' or 'short').
            amount (float): Number of units (or fractions).
            entry_price (float): Entry price of the asset.
            entry_date (pd.Timestamp): Date of the entry.

        Example:
            >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
            >>> pos.type
            'long'
            >>> pos.amount
            10
            >>> pos.entry_price
            100
            >>> pos.entry_date
            Timestamp('2023-01-01 00:00:00')
            >>> pos.closed
            False

            >>> pos = Position('test', 10, 100, pd.Timestamp('2023-01-01'))
            Traceback (most recent call last):
            ...
            ValueError: Position type must be either 'long' or 'short'

        """
        self.type = position_type
        self.amount = amount
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.closed = False
        self.exit_price = None
        self.exit_date = None
        self.pnl = 0.0
        self.stop_loss_price = 0.0

        if position_type not in ["long", "short"]:
            raise ValueError("Position type must be either 'long' or 'short'")

    def close(self, exit_price: float, exit_date: pd.Timestamp) -> None:
        """
        Closes the position and calculates the pnl (profit or loss).

        Args:
            exit_price (float): Exit price.
            exit_date (pd.Timestamp): Exit date.

        Example:
            >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
            >>> pos.close(110, pd.Timestamp('2023-02-01'))
            >>> pos.pnl
            100
            >>> pos.closed
            True

            >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
            >>> pos.close(140, pd.Timestamp('2023-02-01'))
            >>> pos.pnl
            50
            >>> pos.closed
            True

            >>> pos.close(140, pd.Timestamp('2023-02-01'))
            Traceback (most recent call last):
            ...
            ValueError: Position is already closed
        """
        if self.closed:
            raise ValueError("Position is already closed")

        self.exit_price = exit_price
        self.exit_date = exit_date
        self.closed = True

        if self.type == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.amount
        elif self.type == "short":
            self.pnl = (self.entry_price - self.exit_price) * self.amount
