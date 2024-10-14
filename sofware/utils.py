"""
utils.py

Module containing utility functions for the software.
"""

import logging


def calculate_exit_prices(
    position_type, price, stop_loss_pct, take_profit_pct, slippage_pct
):
    if position_type == "long":
        stop_loss = price * (1 - stop_loss_pct)
        take_profit = price * (1 + take_profit_pct)
        adjusted_price = price * (1 + slippage_pct)
    elif position_type == "short":
        stop_loss = price * (1 + stop_loss_pct)
        take_profit = price * (1 - take_profit_pct)
        adjusted_price = price * (1 - slippage_pct)
    else:
        raise ValueError(f"Unknown position type: {position_type}")
    return stop_loss, take_profit, adjusted_price


def calculate_size(price, equity, stop_loss_pct, risk_per_trade):
    atr_stop_loss_dollar = stop_loss_pct * price
    risk_amount = equity * risk_per_trade

    if atr_stop_loss_dollar > risk_amount:
        logging.warning(
            "Stop-loss dollar value exceeds risk amount. Reducing position size."
        )
        return equity / price

    return risk_amount / atr_stop_loss_dollar


def apply_slippage(price, position_type, slippage_pct):
    return (
        price * (1 - slippage_pct)
        if position_type == "long"
        else price * (1 + slippage_pct)
    )


def calculate_proceeds(adjusted_price, amount, transaction_cost):
    return adjusted_price * amount * (1 - transaction_cost)
