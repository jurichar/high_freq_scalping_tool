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

from software.trade_utils import apply_slippage, calculate_size_in_usdt
from software.position import Position


class TradingExecutor:
    """
    Manages the execution of trading signals and the portfolio.
    """

    def __init__(
        self,
        initial_cash,
        transaction_cost,
        leverage,
        slippage_pct,
        risk_per_trade,
    ):
        """
        Initializes the TradingExecutor to manage trades and the portfolio.

        Args:
            initial_cash (float): Starting cash for the portfolio.
            transaction_cost (float): Transaction cost (e.g., 0.001 for 0.1%).
            leverage (float): Leverage factor.
            slippage_pct (float): Slippage percentage.
            risk_per_trade (float): The percentage of the capital you are
            willing to risk per trade.
        """
        self.cash = initial_cash
        self.transaction_cost = transaction_cost
        self.leverage = leverage
        self.slippage_pct = slippage_pct
        self.risk_per_trade = risk_per_trade
        self.positions = []
        self.history = []

    def open_position(
        self,
        position_type: str,
        price: float,
        stop_loss_price: float,
        date: pd.Timestamp,
    ) -> None:
        """
        Opens a position (long or short).

        Args:
            position_type (str): 'long' or 'short'.
            price (float): Entry price.
            date (pd.Timestamp): Entry date.
            stop_loss_price (float): Stop-loss price.

        Example:
            >>> executor = TradingExecutor(
            ...     initial_cash=3000,
            ...     transaction_cost=0.001,
            ...     risk_per_trade=0.02,
            ...     slippage_pct=0,
            ...     leverage=1,
            ... )
            >>> executor.open_position(
            ...     position_type='short',
            ...     price=8611.5,
            ...     stop_loss_price=9156.5,
            ...     date=pd.Timestamp('2023-01-01')
            ... )
            >>> len(executor.positions) == 1
            True

            >>> round(executor.cash, 2)
            2051.94

            >>> executor.open_position('long', 8611.5, 7847, pd.Timestamp('2023-01-02'))
            >>> len(executor.positions) == 2
            True

            >>> round(executor.cash, 2)
            1589.67

            >>> executor.open_position('long', 100, 95, pd.Timestamp('2023-01-04'))
            >>> len(executor.positions) == 3
            True

            >>> round(executor.cash, 2)
            953.8
        """

        try:
            adjusted_price = apply_slippage(
                price,
                position_type,
                self.slippage_pct,
            )
            # ~8611.5$

            size_usdt = calculate_size_in_usdt(
                equity=self.cash,
                risk_per_trade=self.risk_per_trade,
                adjusted_price=adjusted_price,
                stop_loss_price=stop_loss_price,
            )
            # ~948$
            print("Size in USDT: ", size_usdt)

            if size_usdt > self.cash:
                logging.warning(
                    "Not enough cash. Required: %s, Available: %s",
                    size_usdt,
                    self.cash,
                )
                return

            self.cash -= size_usdt
            # 3000 - 948 = 2052
            amount = size_usdt / adjusted_price
            # 948 / 8611.5 = 0.11BTC

            print("Amount: ", amount, "BTC/USDT")

            position = Position(
                position_type=position_type,
                amount=amount,
                entry_price=adjusted_price,
                entry_date=date,
            )

            print("======= Position opened at: ", adjusted_price, "=======")

            position.stop_loss_price = stop_loss_price
            self.positions.append(position)

            self.history.append(
                {
                    "action": "open",
                    "position_type": position_type,
                    "price": adjusted_price,
                    "amount": amount,
                    "date": date,
                }
            )
            logging.debug("Cash after opening position %.2f", self.cash)

        except Exception as e:
            logging.error("Error opening position: %s", e)
            raise RuntimeError(f"Failed to open position due to: {e}") from e

    def close_position(
        self, position: Position, price: float, date: pd.Timestamp
    ) -> None:
        """
        Closes a position and records the transaction.

        Args:
            position (Position): The position to close.
            price (float): The exit price.
            date (pd.Timestamp): The exit date.

        Example:
            >>> executor = TradingExecutor(
            ...     initial_cash=3000,
            ...     transaction_cost=0.001,
            ...     risk_per_trade=0.02,
            ...     slippage_pct=0,
            ...     leverage=1,
            ... )

            >>> executor.open_position(
            ...     'long', 100, 95, pd.Timestamp('2023-01-01')
            ... )

            >>> len(executor.positions) == 1
            True

            >>> position = executor.positions[0]
            >>> executor.close_position(
            ...     position, 110, pd.Timestamp('2023-02-01')
            ... )

            >>> len(executor.positions) == 0
            True
        """

        try:
            adjusted_price = apply_slippage(
                price,
                position.type,
                self.slippage_pct,
            )
            proceeds = adjusted_price * position.amount
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

            logging.info(
                "Closed %s position. PnL: %.2f",
                position.type,
                position.pnl,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to close position due to: {e}") from e

    def has_open_position(self, position_type: str) -> bool:
        """
        Checks if there is an open position of the given type.

        Args:
            position_type (str): 'long' or 'short'

        Returns:
            bool: True if there is an open position, False otherwise.
        """
        return any(
            p.type == position_type and not p.closed for p in self.positions
        )

    def update_positions(self, price, date, atr_stop_loss):
        positions_to_close = []
        for position in self.positions:
            if not position.closed:
                # Update stop-loss for long position
                if position.type == "long":
                    if price > position.entry_price:
                        ATR = atr_stop_loss
                        new_stop_loss = price - 2 * ATR
                        print("--------------- New stop loss: ", new_stop_loss)
                        print(
                            "--------------- Current stop loss: ",
                            position.stop_loss_price,
                        )
                        if new_stop_loss > position.stop_loss_price:
                            position.stop_loss_price = new_stop_loss

                # Update stop-loss for short position
                elif position.type == "short":
                    if price < position.entry_price:
                        ATR = atr_stop_loss
                        print(
                            "Price is less than entry price recalculating SL..."
                        )
                        new_stop_loss = price + 2 * ATR
                        print(
                            "--------------- Old stop loss: ",
                            position.stop_loss_price,
                            "--------------- New stop loss: ",
                            new_stop_loss,
                            "Price: ",
                            price,
                            "ATR: ",
                            ATR,
                        )
                        if new_stop_loss < position.stop_loss_price:
                            position.stop_loss_price = new_stop_loss

                # Check if stop-loss is hit for long position
                if (
                    position.type == "long"
                    and price <= position.stop_loss_price
                ):
                    print(
                        f"Stop-loss atteint pour la position longue à {price}"
                    )
                    self.close_position(position, price, date)
                    positions_to_close.append(position)

                # Check if stop-loss is hit for short position
                elif (
                    position.type == "short"
                    and price >= position.stop_loss_price
                ):
                    print(
                        f"Stop-loss atteint pour la position courte à {price} le SL est à {position.stop_loss_price}"
                    )
                    self.close_position(position, price, date)
                    positions_to_close.append(position)

        for position in positions_to_close:
            self.positions.remove(position)

    def execute_signal(
        self,
        signal,
        price,
        atr_stop_loss,
        date,
    ):
        """
        Execute trading signals by opening or closing positions.
        This handles both Buy Long and Buy Short, and manages exits.

        Args:
            signal (int): Trading signal (1 for Buy Long, -1 for Buy Short).
            price (float): Current price of the asset.
            date (pd.Timestamp): Current timestamp.
            atr_stop_loss (float): Stop-loss based on ATR.

        Example:
            >>> executor = TradingExecutor(
            ...     initial_cash=3000,
            ...     transaction_cost=0.001,
            ...     risk_per_trade=0.02,
            ...     slippage_pct=0,
            ...     leverage=1,
            ... )
            >>> executor.execute_signal(1, 100, 5, pd.Timestamp('2023-01-01'))
        """

        if signal == 1:  # Buy Long signal
            print("Buy Long signal")
            if not self.has_open_position(
                "long"
            ) and not self.has_open_position("short"):
                stop_loss_price = price - atr_stop_loss
                self.open_position(
                    position_type="long",
                    price=price,
                    stop_loss_price=stop_loss_price,
                    date=date,
                )
        elif signal == -1:  # Buy Short signal
            print("Buy Short signal")
            if not self.has_open_position(
                "short"
            ) and not self.has_open_position("long"):
                stop_loss_price = price + atr_stop_loss
                print("Stop loss price: ", stop_loss_price)
                self.open_position(
                    position_type="short",
                    price=price,
                    stop_loss_price=stop_loss_price,
                    date=date,
                )

    def get_total_portfolio_value(self, current_price):
        """
        Calculates the total portfolio value based on the current price.

        Args:
            current_price (float): Current price of the asset.

        Returns:
            float: Total value of the portfolio.

        Example:
            >>> executor = TradingExecutor(
            ...     initial_cash=10000,
            ...     transaction_cost=0.001,
            ...     risk_per_trade=0.01,
            ...     slippage_pct=0.005,
            ...     leverage=1,
            ... )
            >>> executor.get_total_portfolio_value(110)
            10000.0
            >>> executor.open_position(
            ...     'long', 8611.5, 7847, pd.Timestamp('2023-01-02')
            ... )
            >>> round(executor.get_total_portfolio_value(9000), 2)
            10042.78
        """
        try:
            position_value = 0.0
            for position in self.positions:
                amount = position.amount
                if position.type == "long":
                    profit = (current_price - position.entry_price) * amount
                    position_value += position.entry_price * amount + profit
                elif position.type == "short":
                    profit = (position.entry_price - current_price) * amount
                    position_value += position.entry_price * amount + profit
            total_value = self.cash + position_value
            return total_value
        except (AttributeError, TypeError, ValueError) as e:
            logging.error("Error calculating total portfolio value: %s", e)
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
                    f" - {position.type.capitalize()} {position.amount}\
                        shares at ${position.entry_price:.2f}"
                )
            print(f"Total Portfolio Value: ${total_value:.2f}")
            print("=" * 30 + "\n")
        except (AttributeError, TypeError, ValueError) as e:
            logging.error("Error displaying portfolio: %s", e)
