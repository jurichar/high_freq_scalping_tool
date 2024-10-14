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
        >>> pos = Position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.check_exit_conditions(120, 90)
        True
        >>> pos.check_exit_conditions(120)
        True
        >>> pos = Position('short', 5, 150, pd.Timestamp('2023-01-01'))
        >>> pos.update_stop_loss_take_profit(0.05, 0.1)
        >>> pos.check_exit_conditions(160, 130)
        False
        >>> pos.check_exit_conditions(130)
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
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 1
        True
        >>> executor.cash < 10000
        True
        >>> executor.open_position('short', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 2
        True

        >>> executor = TradingExecutor(initial_cash=100)
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> len(executor.positions) == 0
        True
        """

        try:
            if stop_loss_pct <= 0 or take_profit_pct <= 0:
                logging.error("Stop-loss and take-profit percentages must be positive.")
                return

            atr_stop_loss_dollar = stop_loss_pct * price
            print(f"Price: {price}")
            print(f"Stop_Loss_Pct: {stop_loss_pct}")
            print(f"ATR_Stop_Loss_Dollar: {atr_stop_loss_dollar}")
            equity = self.get_total_portfolio_value(price)
            print(f"Equity: {equity}, Risk Amount: {equity * self.risk_per_trade}")

            risk_amount = equity * self.risk_per_trade
            print(f"Risk Amount: {risk_amount}")

            position_size = risk_amount / atr_stop_loss_dollar
            print(
                f"ATR_Stop_Loss_Dollar: {atr_stop_loss_dollar}, Position Size: {position_size}"
            )

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
            print(f"Total Cost: {total_cost}")
            print(f"Margin Required: {margin_required}")

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
            print(f"Cash after opening position: ${self.cash:.2f}")

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
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> position = executor.positions[0]
        >>> position.update_stop_loss_take_profit(0.05, 0.1)
        >>> executor.check_positions(120, pd.Timestamp('2023-02-01'))
        >>> len(executor.positions) == 0
        True
        """
        for position in self.positions[:]:
            if position.check_exit_conditions(high_price, low_price):
                logging.info(
                    f"Exit conditions met for {position.type} position at {price}."
                )
                self.close_position(position, price, date)

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

        if signal == 1:
            # Close existing short positions before opening long
            short_positions = [p for p in self.positions if p.type == "short"]
            for position in short_positions:
                self.close_position(position, price, date)

            # Open new long position if not already in a long position
            if not any(p.type == "long" for p in self.positions):
                self.open_position(
                    "long", price, date, atr_stop_loss / price, atr_take_profit / price
                )

        elif signal == -1:
            # Close existing long positions before opening short
            long_positions = [p for p in self.positions if p.type == "long"]
            for position in long_positions:
                self.close_position(position, price, date)

            # Open new short position if not already in a short position
            if not any(p.type == "short" for p in self.positions):
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

        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.open_position('long', 10, 100, pd.Timestamp('2023-01-01'))
        >>> executor.get_total_portfolio_value(110)
        9099.0

        >>> executor = TradingExecutor(initial_cash=10000)
        >>> executor.open_position('short', 10, 100, pd.Timestamp('2023-01-01'))
        >>> executor.get_total_portfolio_value(90)
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
