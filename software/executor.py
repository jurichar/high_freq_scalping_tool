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

from software.trade_utils import (
    apply_slippage,
    calculate_proceeds,
    calculate_size,
)


class Position:

    def __init__(
        self,
        position_type,
        amount,
        entry_price,
        entry_date,
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
        self.closed = False
        self.exit_price = None
        self.exit_date = None
        self.pnl = 0.0

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
        """
        self.exit_price = exit_price
        self.exit_date = exit_date
        self.closed = True

        if self.type == "long":
            self.pnl = (self.exit_price - self.entry_price) * self.amount
        elif self.type == "short":
            self.pnl = (self.entry_price - self.exit_price) * self.amount


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
        If I have $10000 and I want to risk 1% of my equity on a trade of a stock priced at $100,
        I can buy 50 shares with a stop-loss of 5%.

        Args:
            price (float): Current price of the asset.
            stop_loss_pct (float): Stop-loss percentage.

        Returns:
            float: The maximum position size.

        Example:
            >>> executor = TradingExecutor(initial_cash=10000)
            >>> executor.calculate_position_size(100, 0.05)
            50.0
        """
        return calculate_size(
            price=price,
            equity=self.get_total_portfolio_value(price),
            stop_loss_pct=stop_loss_pct,
            risk_per_trade=self.risk_per_trade,
        )

    def open_position(
        self,
        position_type: str,
        price: float,
        date: pd.Timestamp,
        stop_loss_pct: float,
    ) -> None:
        """
        Opens a long or short position with dynamic sizing based on risk.

        Args:
            position_type (str): Type of position ('long' or 'short').
            price (float): Asset price.
            date (pd.Timestamp): Transaction date.
            stop_loss_pct (float): Stop-loss percentage.

        Example:
            >>> executor = TradingExecutor(initial_cash=10000)
            >>> executor.open_position(position_type='long', price=100, date=pd.Timestamp('2023-01-01'), stop_loss_pct=0.05)
            >>> len(executor.positions) == 1
            True
            >>> executor.cash

            >>> executor.open_position('short', 100, pd.Timestamp('2023-01-01'), 0.05)
            >>> len(executor.positions) == 2
            True

            >>> executor = TradingExecutor(initial_cash=100)
            >>> executor.open_position('long', 100, pd.Timestamp('2023-01-01'), 0.05)
            >>> len(executor.positions) == 0
            True
        """

        try:
            position_size = self.calculate_position_size(price, stop_loss_pct)
            adjusted_price = apply_slippage(price, position_type, self.slippage_pct)
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
            >>> executor.open_position('long', 10, pd.Timestamp('2023-01-01'), 0.05)
            >>> len(executor.positions) == 1
            True
            >>> position = executor.positions[0]
            >>> executor.close_position(position, 110, pd.Timestamp('2023-02-01'))
            >>> len(executor.positions) == 0
            True
        """
        try:
            adjusted_price = apply_slippage(price, position.type, self.slippage_pct)
            proceeds = calculate_proceeds(
                adjusted_price, position.amount, self.transaction_cost
            )
            position.close(adjusted_price, date)
            self.cash += proceeds
            self.history.append(
                {
                    "action": "close",
                    "position_type": position.type,
                    "price": adjusted_price,
                    "amount": position.amount,
                    "date": date,
                    "pnl": position.pnl,
                }
            )
            self.positions.remove(position)
        except Exception as e:
            logging.error(f"Error closing position: {e}")

    def has_open_position(self, position_type: str) -> bool:
        """
        Checks if there is an open position of the given type.

        Args:
            position_type (str): 'long' or 'short'

        Returns:
            bool: True if there is an open position, False otherwise.
        """
        return any(p.type == position_type and not p.closed for p in self.positions)

    def execute_signal(self, signal, price, date, atr_stop_loss):
        """
        Execute trading signals by opening or closing positions.
        This handles both Buy Long and Buy Short, and manages exits.

        Args:
            signal (int): Trading signal (1 for Buy Long, -1 for Buy Short, 2 for Exit Long, -2 for Exit Short).
            price (float): Current price of the asset.
            date (pd.Timestamp): Current timestamp.
            high_price (float): High price for the period.
            low_price (float): Low price for the period.
            atr_stop_loss (float): Stop-loss based on ATR.
            atr_take_profit (float): Take-profit based on ATR.

        Example:
            >>> executor = TradingExecutor(initial_cash=10000)
            >>> executor.execute_signal(1, 100, pd.Timestamp('2023-01-01'), 0.05)
        """

        if signal == 1:  # Buy Long signal
            if not self.has_open_position("long"):
                self.open_position("long", price, date, atr_stop_loss / price)
        elif signal == -1:  # Buy Short signal
            if not self.has_open_position("short"):
                self.open_position("short", price, date, atr_stop_loss / price)
        elif signal == 2:  # Close Long signal
            for position in self.positions[:]:
                if position.type == "long" and not position.closed:
                    self.close_position(position, price, date)
        elif signal == -2:  # Close Short signal
            for position in self.positions[:]:
                if position.type == "short" and not position.closed:
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
            >>> executor.open_position('long', 10, pd.Timestamp('2023-01-01'), 0.05)
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
