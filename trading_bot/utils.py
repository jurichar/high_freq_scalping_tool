"""
utils.py

Module containing utility functions for the trading bot.


"""


def calculate_percentage_return(initial_cash, final_value):
    """
    Args:
        initial_cash (float): The initial cash value.
        final_value (float): The final value of the portfolio.
    Returns:
        float: Percentage return on investment.

    Example:
    >>> calculate_percentage_return(1000, 1200)
    20.0
    """
    return ((final_value - initial_cash) / initial_cash) * 100


def calculate_max_drawdown(equity_curve):
    """
    Args:
        equity_curve (pd.Series): The equity curve of the portfolio over time.
    Returns:
        float: Maximum drawdown percentage.

    Example:
    >>> equity_curve = pd.Series([100, 110, 90, 120, 80])
    >>> calculate_max_drawdown(equity_curve)
    -20.0
    """
    roll_max = equity_curve.cummax()
    drawdown = (equity_curve - roll_max) / roll_max
    return drawdown.min() * 100


def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """
    Args:
        returns (pd.Series): The daily or weekly returns of the strategy.
        risk_free_rate (float): The risk-free rate, e.g., return on Treasury bills.
    Returns:
        float: The Sharpe ratio.

    Example:
    >>> returns = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015])
    >>> calculate_sharpe_ratio(returns)
    1.224744871391589
    """
    excess_returns = returns - risk_free_rate
    return excess_returns.mean() / excess_returns.std()


def calculate_sortino_ratio(returns, risk_free_rate=0):
    """
    Args:
        returns (pd.Series): The daily or weekly returns of the strategy.
        risk_free_rate (float): The risk-free rate.
    Returns:
        float: The Sortino ratio.

    Example:
    >>> returns = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015])
    >>> calculate_sortino_ratio(returns)
    1.414213562373095
    """
    downside_returns = returns[returns < 0]
    return (returns.mean() - risk_free_rate) / downside_returns.std()
