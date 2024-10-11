"""
executor.py

Module to execute trading orders based on generated signals.

This module executes buy and sell orders based on the trading signals
produced by the strategy.

Functions:
- execute_orders: Executes buy/sell orders based on signals.
"""

import logging
import pandas as pd


class TradingExecutor:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.stock_balance = 0
        self.history = []

    def buy(self, price, amount):
        """
        Buy a specified amount of shares at the given price.

        Args:
            price (float): The price of one share.
            amount (int): The number of shares to buy.

        Example:
            >>> executor = TradingExecutor(initial_cash=1000)
            >>> executor.buy(price=10, amount=5)
            >>> executor.cash
            950
            >>> executor.stock_balance
            5
        """

        total_cost = price * amount
        if self.cash >= total_cost:
            self.cash -= total_cost
            self.stock_balance += amount
            self.history.append(f"Bought {amount} shares at ${price:.2f} each")
        else:
            return

    def sell(self, price, amount):
        """
        Sell a specified amount of shares at the given price.

        Args:
            price (float): The price of one share.
            amount (int): The number of shares to sell.

        Example:
            >>> executor = TradingExecutor(initial_cash=1000)
            >>> executor.stock_balance = 10
            >>> executor.sell(price=20, amount=5)
            >>> executor.cash
            1100
            >>> executor.stock_balance
            5
        """
        if self.stock_balance >= amount:
            total_sale = price * amount
            self.cash += total_sale
            self.stock_balance -= amount
            self.history.append(f"Sold {amount} shares at ${price:.2f} each")
        else:
            return

    def execute_orders(self, signals):
        """
        Execute buy/sell orders based on the signals.

        Args:
            signals (pd.DataFrame): DataFrame with 'Signal' column indicating buy/sell actions.

        Example:
            >>> signals = pd.DataFrame({"Signal": [1, -1, 1], "Close": [100, 110, 105]})
            >>> executor = TradingExecutor(initial_cash=1000)
            >>> executor.execute_orders(signals)
            >>> executor.cash
            905
            >>> executor.stock_balance
            1
        """
        for index, row in signals.iterrows():
            if row["Signal"] == 1:
                self.buy(price=row["Close"], amount=1)
            elif row["Signal"] == -1:
                self.sell(price=row["Close"], amount=1)

    def display_portfolio(self, latest_price):
        """
        Display the current status of the portfolio.
        """
        total_value = self.cash + self.stock_balance * latest_price
        print(f"Cash: ${self.cash:.2f}")
        print(f"Stock Balance: {self.stock_balance} shares")
        print(f"Total Portfolio Value: ${total_value:.2f}")
