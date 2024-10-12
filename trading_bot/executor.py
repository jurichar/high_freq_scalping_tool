"""
executor.py

Module to execute trading orders based on generated signals.

This module executes buy and sell orders based on the trading signals
produced by the strategy.

Functions:
- check_stop_take_profit: Check if the stop-loss or take-profit conditions are met.
- execute_orders: Executes buy/sell orders based on signals.
- display_portfolio: Displays the current portfolio value.
"""

import logging
import pandas as pd


class TradingExecutor:
    def __init__(
        self,
        initial_cash,
        transaction_cost=0.001,
        leverage=1,
        stop_loss=None,
        take_profit=None,
    ):
        """
        Trading executor handles the buy/sell transactions and manages the portfolio.

        Args:
            initial_cash (float): Initial cash amount.
            transaction_cost (float): Transaction cost as a fraction of the trade (e.g., 0.001 for 0.1%).
            leverage (float): Leverage factor (e.g., 1 = no leverage, 2 = 2x leverage).
            stop_loss (float): Optional stop-loss percentage (e.g., 0.05 for 5% stop-loss).
            take_profit (float): Optional take-profit percentage (e.g., 0.1 for 10% take-profit).
        """
        self.cash = initial_cash
        self.stock_balance = 0
        self.transaction_cost = transaction_cost
        self.leverage = leverage
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.history = []
        self.last_buy_price = None

    def buy(self, price, amount):
        """
        Buy a specified amount of shares.

        Args:
            price (float): Price of the stock.
            amount (int): Number of shares to buy.
        """
        total_cost = price * amount * (1 + self.transaction_cost)
        total_cost /= self.leverage
        if self.cash >= total_cost:
            self.cash -= total_cost
            self.stock_balance += amount
            self.last_buy_price = price
        else:
            logging.warning("Not enough cash to buy.")

    def sell(self, price, amount=1):
        """Sell a specified amount of shares.

        Args:
            price (float): Price of the stock.
            amount (int): Number of shares to sell.
        """
        if self.stock_balance >= amount:
            total_gain = price * amount * (1 - self.transaction_cost)
            total_gain *= self.leverage
            self.cash += total_gain
            self.stock_balance -= amount
        else:
            logging.warning("Not enough stock to sell.")

    def check_stop_take_profit(self, price):
        """
        Check if the stop-loss or take-profit conditions are met.

        Args:
            price (float): Current stock price.
        Returns:
            bool: True if the stock should be sold.
        """
        if self.last_buy_price is None:
            return False

        if self.stop_loss and price <= self.last_buy_price * (1 - self.stop_loss):
            logging.info(f"Stop-loss triggered at {price}.")
            return True
        if self.take_profit and price >= self.last_buy_price * (1 + self.take_profit):
            logging.info(f"Take-profit triggered at {price}.")
            return True
        return False

    def execute_orders(self, signals):
        """
        Execute buy/sell orders based on the signals.

        Args:
            signals (pd.DataFrame): DataFrame with 'Signal' column indicating buy/sell actions.
        """
        for index, row in signals.iterrows():
            if row["Signal"] == 1:
                self.buy(price=row["Close"], amount=1)
            elif row["Signal"] == -1 or self.check_stop_take_profit(row["Close"]):
                self.sell(price=row["Close"], amount=1)

    def display_portfolio(self, latest_price):
        """Display the current portfolio value."""
        total_value = self.cash + self.stock_balance * latest_price
        print(f"Cash: ${self.cash:.2f}")
        print(f"Stock Balance: {self.stock_balance} shares")
        print(f"Total Portfolio Value: ${total_value:.2f}")
