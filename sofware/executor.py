"""
executor.py

Module to execute trading orders based on generated signals.

This module manages the execution of buy and sell orders, portfolio tracking,
and applies stop-loss and take-profit mechanisms using a `Position` class.

Classes:
- Position: Represents an individual position (long or short).
- TradingExecutor: Manages trade execution and the portfolio.
"""

import logging
import pandas as pd
from datetime import datetime


class Position:
    def __init__(
        self,
        position_type,
        amount,
        entry_price,
        entry_date,
        stop_loss=None,
        take_profit=None,
    ):
        """
        Initializes a position.

        Args:
            position_type (str): Type of position ('long' or 'short').
            amount (int): Number of shares.
            entry_price (float): Entry price.
            entry_date (pd.Timestamp): Entry date.
            stop_loss (float, optional): Stop-loss level.
            take_profit (float, optional): Take-profit level.
        """
        self.type = position_type
        self.amount = amount
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.closed = False
        self.exit_price = None
        self.exit_date = None
        self.profit_loss = 0.0

    def update_stop_loss_take_profit(
        self, stop_loss_pct: float, take_profit_pct: float
    ) -> None:
        """
        Updates the stop-loss and take-profit levels based on the entry price.

        Args:
            stop_loss_pct (float): Stop-loss percentage.
            take_profit_pct (float): Take-profit percentage.

        Example:
        >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.stop_loss
        95.0
        >>> pos.take_profit
        110.00000000000001
        >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.stop_loss
        157.5
        >>> pos.take_profit
        135.0
        """
        if self.type == "long":
            self.stop_loss = (
                self.entry_price * (1 - stop_loss_pct) if stop_loss_pct else None
            )
            self.take_profit = (
                self.entry_price * (1 + take_profit_pct) if take_profit_pct else None
            )
        elif self.type == "short":
            self.stop_loss = (
                self.entry_price * (1 + stop_loss_pct) if stop_loss_pct else None
            )
            self.take_profit = (
                self.entry_price * (1 - take_profit_pct) if take_profit_pct else None
            )

    def check_exit_conditions(self, current_price: float) -> bool:
        """
        Checks if the stop-loss or take-profit conditions are met.

        Args:
            current_price (float): Current price of the asset.

        Returns:
            bool: True if the position should be closed, False otherwise.

        Example:
        >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.check_exit_conditions(110)
        False
        >>> pos.check_exit_conditions(120)
        True
        >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.check_exit_conditions(140)
        False
        >>> pos.check_exit_conditions(130)
        True
        """
        if self.closed:
            return False
        if self.type == "long":
            if self.stop_loss is not None and current_price <= self.stop_loss:
                return True
            if self.take_profit is not None and current_price >= self.take_profit:
                return True
        elif self.type == "short":
            if self.stop_loss is not None and current_price >= self.stop_loss:
                return True
            if self.take_profit is not None and current_price <= self.take_profit:
                return True
        return False

    def close(self, exit_price: float, exit_date: pd.Timestamp) -> None:
        """
        Closes the position and calculates the profit or loss.

        Args:
            exit_price (float): Exit price.
            exit_date (pd.Timestamp): Exit date.

        Example:
        >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> pos.close(110, pd.Timestamp('2023-02-01'))
        >>> pos.profit_loss
        100
        >>> pos.closed
        True

        >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
        >>> pos.close(140, pd.Timestamp('2023-02-01'))
        >>> pos.profit_loss
        50
        >>> pos.closed
        True
        """
        self.exit_price = exit_price
        self.exit_date = exit_date
        self.closed = True

        if self.type == "long":
            self.profit_loss = (self.exit_price - self.entry_price) * self.amount
        elif self.type == "short":
            self.profit_loss = (self.entry_price - self.exit_price) * self.amount


class TradingExecutor:
    def __init__(
        self,
        initial_cash,
        transaction_cost=0.001,
        leverage=1,
        stop_loss_pct=None,
        take_profit_pct=None,
        trailing_pct=None,
    ):
        """
        Initializes the TradingExecutor to manage trades and the portfolio.

        Args:
            initial_cash (float): Initial cash amount.
            transaction_cost (float): Transaction cost as a fraction of the trade (e.g., 0.001 for 0.1%).
            leverage (float): Leverage factor (e.g., 1 = no leverage, 2 = leverage x2).
            stop_loss_pct (float): Stop-loss percentage (e.g., 0.05 for a 5% stop-loss).
            take_profit_pct (float): Take-profit percentage (e.g., 0.1 for a 10% take-profit).
        """
        self.cash = initial_cash
        self.transaction_cost = transaction_cost
        self.leverage = leverage
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trailing_pct = trailing_pct
        self.positions = []
        self.history = []

    def open_position(
        self, position_type: str, amount: int, price: float, date: pd.Timestamp
    ) -> None:
        """
        Opens a long or short position.

        Args:
            position_type (str): Type of position ('long' or 'short').
            price (float): Asset price.
            amount (int): Quantity to buy or sell.
            date (pd.Timestamp): Transaction date.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 1
        True
        >>> executor.cash < 10000
        True
        >>> executor.open_position('short', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 2
        True
        """
        try:
            total_cost = price * amount * (1 + self.transaction_cost)
            margin_required = total_cost / self.leverage
            if self.cash < margin_required:
                logging.warning("Insufficient funds to open position.")
                return
            self.cash -= margin_required
            position = Position(
                position_type=position_type,
                amount=amount * self.leverage,
                entry_price=price,
                entry_date=date,
            )
            position.update_stop_loss_take_profit(
                self.stop_loss_pct, self.take_profit_pct
            )
            self.positions.append(position)
            self.history.append(
                {
                    "action": "open",
                    "position_type": position_type,
                    "price": price,
                    "amount": amount * self.leverage,
                    "date": date,
                }
            )

        except Exception as e:
            logging.error(f"Error opening position: {e}")

    def close_position(
        self, position: Position, price: float, date: pd.Timestamp
    ) -> None:
        """
        Closes an existing position.

        Args:
            position (Position): Position object to close.
            price (float): Current price of the asset.
            date (pd.Timestamp): Transaction date.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 1
        True
        >>> position = executor.positions[0]
        >>> executor.close_position(position, 110, pd.Timestamp('2023-02-01'))
        >>> len(executor.positions) == 0
        True
        """
        try:
            amount = position.amount
            proceeds = price * amount * (1 - self.transaction_cost)
            position.close(price, date)
            self.cash += proceeds
            self.history.append(
                {
                    "action": "close",
                    "position_type": position.type,
                    "price": price,
                    "amount": amount,
                    "date": date,
                    "profit_loss": position.profit_loss,
                }
            )
            self.positions.remove(position)
        except Exception as e:
            logging.error(f"Error closing position: {e}")

    def check_positions(self, price, date):
        """
        Checks positions to determine if stop-loss or take-profit conditions are met.

        Args:
            price (float): Current price of the asset.
            date (pd.Timestamp): Current date.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> position = executor.positions[0]
        >>> position.update_stop_loss_take_profit(0.05, 0.1)
        >>> executor.check_positions(120, pd.Timestamp('2023-02-01'))
        >>> len(executor.positions) == 0
        True
        """
        for position in self.positions[:]:
            if position.check_exit_conditions(price):
                logging.info(
                    f"Exit conditions met for {position.type} position at {price}."
                )
                self.close_position(position, price, date)

    def execute_signal(self, signal, price, date):
        """
        Executes a trading signal.

        Args:
        signal (int): Trading signal.
        1  - Enter Long
        2  - Exit Long
        -1 - Enter Short
        -2 - Exit Short
        0  - Hold
        price (float): Current price of the asset.
        date (pd.Timestamp): Current date.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.execute_signal(1, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 1
        True
        >>> executor.execute_signal(2, 110, pd.Timestamp('2023-02-01'))
        >>> len(executor.positions) == 0
        True

        >>> executor.execute_signal(-1, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 1
        True
        >>> executor.execute_signal(-2, 90, pd.Timestamp('2023-02-01'))
        >>> len(executor.positions) == 0
        True
        """
        self.check_positions(price, date)

        if signal == 1:
            short_positions = [p for p in self.positions if p.type == "short"]
            for position in short_positions:
                self.close_position(position, price, date)
            if not any(p.type == "long" for p in self.positions):
                self.open_position("long", 1, price, date)

        elif signal == 2:
            long_positions = [p for p in self.positions if p.type == "long"]
            for position in long_positions:
                self.close_position(position, price, date)

        elif signal == -1:
            long_positions = [p for p in self.positions if p.type == "long"]
            for position in long_positions:
                self.close_position(position, price, date)
            if not any(p.type == "short" for p in self.positions):
                self.open_position("short", 1, price, date)

        elif signal == -2:
            short_positions = [p for p in self.positions if p.type == "short"]
            for position in short_positions:
                self.close_position(position, price, date)

    def get_total_portfolio_value(self, current_price):
        """
        Calculates the total portfolio value.

        Args:
            current_price (float): Current price of the asset.

        Returns:
            float: Total value of the portfolio.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.get_total_portfolio_value(110)
        10000.0
        """
        try:
            position_value = 0.0
            for position in self.positions:
                amount = position.amount
                if position.type == "long":
                    position_value += (current_price - position.entry_price) * amount
                elif position.type == "short":
                    position_value += (position.entry_price - current_price) * amount
            total_value = self.cash + position_value
            return total_value
        except Exception as e:
            logging.error(f"Error calculating portfolio value: {e}")
            return None

    def display_portfolio(self, current_price):
        """
        Displays the current state of the portfolio.

        Args:
            current_price (float): Current price of the asset.

        Example:
        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.display_portfolio(110)
        <BLANKLINE>
        ==============================
        Current Portfolio Status:
        Cash: $10000.00
        Open Positions: 0
        Total Portfolio Value: $10000.00
        ==============================
        <BLANKLINE>
        """
        try:
            total_value = self.get_total_portfolio_value(current_price)
            print("\n" + "=" * 30)
            print("Current Portfolio Status:")
            print(f"Cash: ${self.cash:.2f}")
            print(f"Open Positions: {len(self.positions)}")
            for position in self.positions:
                print(
                    f" - {position.type.capitalize()} {position.amount} shares at ${position.entry_price:.2f}"
                )
            print(f"Total Portfolio Value: ${total_value:.2f}")
            print("=" * 30 + "\n")
        except Exception as e:
            logging.error(f"Error displaying portfolio: {e}")