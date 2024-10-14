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

    def check_exit_conditions(self, high_price: float, low_price: float) -> bool:
        """
        Checks if the stop-loss or take-profit conditions are met.

        Args:
            current_price (float): Current price of the asset.
            high_price (float): High price of the asset in this period.
            low_price (float): Low price of the asset in this period.

        Returns:
            bool: True if the position should be closed, False otherwise.

        Example:
            >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
            >>> pos.check_exit_conditions(140, 160)
            False

            >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
            >>> pos.take_profit = 110
            >>> pos.check_exit_conditions(120, 90)
            True

            >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
            >>> pos.stop_loss = 140
            >>> pos.check_exit_conditions(140, 160)
            True
        """
        if self.closed:
            return False

        epsilon = 1e-6

        if self.type == "long":
            if self.stop_loss is not None and low_price <= self.stop_loss + epsilon:
                return True
            if (
                self.take_profit is not None
                and high_price >= self.take_profit - epsilon
            ):
                return True
        elif self.type == "short":
            if self.stop_loss is not None and high_price >= self.stop_loss - epsilon:
                return True
            if self.take_profit is not None and low_price <= self.take_profit + epsilon:
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
        trailing_pct=None,
        slippage_pct=0.0005,
        risk_per_trade=0.01,
    ):
        """
        Initializes the TradingExecutor to manage trades and the portfolio.

        Args:
            initial_cash (float): Initial cash amount.
            transaction_cost (float): Transaction cost as a fraction of the trade (e.g., 0.001 for 0.1%).
            leverage (float): Leverage factor (e.g., 1 = no leverage, 2 = leverage x2).
            trailing_pct (float, optional): Trailing stop-loss percentage.
            slippage_pct (float): Slippage percentage.
            risk_per_trade (float): Fraction of portfolio to risk per trade (e.g., 0.01 for 1%).
        """
        self.cash = initial_cash
        self.transaction_cost = transaction_cost
        self.leverage = leverage
        self.trailing_pct = trailing_pct
        self.positions = []
        self.history = []
        self.slippage_pct = slippage_pct
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, price: float, stop_loss_pct: float) -> float:
        """
        Calculates the optimal position size based on available risk and cash.

        Args:
            price (float): Current price of the asset.
            stop_loss_pct (float): Stop-loss percentage.

        Returns:
            float: The maximum position size.
        """
        atr_stop_loss_dollar = stop_loss_pct * price
        equity = self.get_total_portfolio_value(price)
        risk_amount = equity * self.risk_per_trade

        if atr_stop_loss_dollar > risk_amount:
            logging.warning(
                "Stop-loss dollar value exceeds risk amount. Reducing position size."
            )
            return self.cash / price

        position_size = risk_amount / atr_stop_loss_dollar
        return position_size

    def open_position(
        self,
        position_type: str,
        price: float,
        date: pd.Timestamp,
        stop_loss_pct: float,
        take_profit_pct: float,
    ) -> None:
        """
        Opens a long or short position with dynamic sizing based on risk.

        Args:
            position_type (str): Type of position ('long' or 'short').
            price (float): Asset price.
            date (pd.Timestamp): Transaction date.
            stop_loss_pct (float): Stop-loss percentage.
            take_profit_pct (float): Take-profit percentage.

        Example:
            >>> executor = TradingExecutor(initial_cash=10000)
            >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'), 0.05, 0.1)
            >>> len(executor.positions) == 1
            True
            >>> executor.cash < 10000
            True
            >>> executor.open_position('short', 10, 100, pd.Timestamp('2023-01-01'))
            >>> len(executor.positions) == 2
            True

            >>> executor = TradingExecutor(initial_cash=100)
            >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'), 0.05, 0.1)
            >>> len(executor.positions) == 0
            True
        """

        try:
            position_size = self.calculate_position_size(price, stop_loss_pct)

            if position_size <= 0:
                logging.warning("Calculated position size is zero. Skipping trade.")
                return

            if position_type == "long":
                stop_loss = price * (1 - stop_loss_pct)
                take_profit = price * (1 + take_profit_pct)
                adjusted_price = price * (1 + self.slippage_pct)
            elif position_type == "short":
                stop_loss = price * (1 + stop_loss_pct)
                take_profit = price * (1 - take_profit_pct)
                adjusted_price = price * (1 - self.slippage_pct)
            else:
                logging.error(f"Unknown position type: {position_type}")
                return

            total_cost = adjusted_price * position_size * (1 + self.transaction_cost)
            margin_required = total_cost / self.leverage
            logging.info(f"Total Cost: {total_cost}")
            logging.info(f"Margin Required: {margin_required}")

            if margin_required > self.cash:
                logging.warning(
                    f"Reducing position size due to insufficient funds. Margin required: {margin_required}, Available cash: {self.cash}"
                )
                position_size = (self.cash * self.leverage) / (
                    price * (1 + self.transaction_cost)
                )
                total_cost = price * position_size * (1 + self.transaction_cost)
                margin_required = total_cost / self.leverage

            if position_size <= 0:
                logging.warning("Position size too small. Skipping trade.")
                return

            self.cash -= margin_required
            logging.info(f"Cash after opening position: ${self.cash:.2f}")

            position = Position(
                position_type=position_type,
                amount=position_size,
                entry_price=price,
                entry_date=date,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )
            self.positions.append(position)

            self.history.append(
                {
                    "action": "open",
                    "position_type": position_type,
                    "price": price,
                    "amount": position_size,
                    "date": date,
                }
            )
            logging.info(
                f"{date}: Opened {position_type} position for {position_size} shares at ${price:.2f}"
            )
            logging.debug(f"Cash after opening position: ${self.cash:.2f}")

        except Exception as e:
            logging.error(f"Error opening position: {e}")
            raise RuntimeError(f"Failed to open position due to: {e}")

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
            >>> executor.open_position('long', 10, pd.Timestamp('2023-01-01'), 0.05, 0.1)
            >>> len(executor.positions) == 1
            True
            >>> position = executor.positions[0]
            >>> executor.close_position(position, 110, pd.Timestamp('2023-02-01'))
            >>> len(executor.positions) == 0
            True
        """
        try:
            amount = position.amount

            if position.type == "long":
                adjusted_price = price * (1 - self.slippage_pct)
            elif position.type == "short":
                adjusted_price = price * (1 + self.slippage_pct)
            else:
                logging.error(f"Unknown position type: {position.type}")
                return

            proceeds = adjusted_price * amount * (1 - self.transaction_cost)
            position.close(adjusted_price, date)
            self.cash += proceeds
            self.history.append(
                {
                    "action": "close",
                    "position_type": position.type,
                    "price": adjusted_price,
                    "amount": amount,
                    "date": date,
                    "profit_loss": position.profit_loss,
                }
            )
            self.positions.remove(position)
        except Exception as e:
            logging.error(f"Error closing position: {e}")

    def check_positions(self, price, date, high_price, low_price):
        """
        Checks positions to determine if stop-loss or take-profit conditions are met.

        Args:
            price (float): Current price of the asset.
            date (pd.Timestamp): Current date.

        Example:
            >>> executor = TradingExecutor(initial_cash=10000)
            >>> executor.open_position('long', 10, pd.Timestamp('2023-01-01'), 0.05, 0.1)
            >>> position = executor.positions[0]
            >>> executor.check_positions(120, pd.Timestamp('2023-02-01'), 120, 90)
            >>> len(executor.positions) == 0
            True
        """
        for position in self.positions[:]:
            if position.check_exit_conditions(high_price, low_price):
                logging.info(
                    f"Exit conditions met for {position.type} position at {price}."
                )
                self.close_position(position, price, date)

    def has_open_position(self, position_type: str) -> bool:
        """
        Checks if there is an open position of the given type.

        Args:
            position_type (str): 'long' or 'short'

        Returns:
            bool: True if there is an open position, False otherwise.
        """
        return any(p.type == position_type and not p.closed for p in self.positions)

    def execute_signal(
        self, signal, price, date, high_price, low_price, atr_stop_loss, atr_take_profit
    ):
        """
        Executes a trading signal.

        Args:
            signal (int): Trading signal.
                1  - Enter Long
                -1 - Enter Short
                0  - Hold
            price (float): Current price of the asset.
            date (pd.Timestamp): Current date.
            high_price (float): High price of the asset in this period.
            low_price (float): Low price of the asset in this period.
            atr_stop_loss (float): ATR-based stop-loss value.
            atr_take_profit (float): ATR-based take-profit value.
        """
        self.check_positions(price, date, high_price, low_price)

        if signal == 1 and not self.has_open_position("long"):
            self.open_position(
                "long", price, date, atr_stop_loss / price, atr_take_profit / price
            )

        elif signal == -1 and not self.has_open_position("short"):
            self.open_position(
                "short", price, date, atr_stop_loss / price, atr_take_profit / price
            )

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
            >>> executor.open_position('long', 10, pd.Timestamp('2023-01-01'), 0.05, 0.1)
            >>> executor.get_total_portfolio_value(110)
            9099.0
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
