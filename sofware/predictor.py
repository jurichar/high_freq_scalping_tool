# Module to predict stock prices
"""
predictor.py

Module for predicting stock prices using machine learning models.

This module provides functions to train and evaluate machine learning models for predicting stock prices.

Functions:
- prepare_data: Prepare the stock data for training a machine learning model.
- train_random_forest: Train a Random Forest model to predict stock prices.
- evaluate_model: Evaluate the performance of a machine learning model.

"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error


def prepare_data(data: pd.DataFrame, target: str = "Close", window: int = 5):
    """
    Prepare the stock data for training a machine learning model.

    Args:
        data (pd.DataFrame): The stock data.
        target (str): The target variable to predict.
        window (int): The window size for the rolling window features.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple containing the features and target variable.

    Example:
        >>> data = pd.DataFrame({'Close': [1, 2, 3, 4, 5]})
        >>> X, y = prepare_data(data, target='Close', window=2)
        >>> X.shape
        (3, 2)
        >>> y.shape
        (3,)
    """
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[target].values[i : i + window])
        y.append(data[target].values[i + window])
    return np.array(X), np.array(y)


def train_random_forest(data: pd.DataFrame, target: str = "Close", window: int = 5):
    """
    Train a Random Forest model to predict stock prices.

    Args:
        data (pd.DataFrame): The stock data.
        target (str): The target variable to predict.
        window (int): The window size for the rolling window features.

    Returns:
        RandomForestRegressor: A trained Random Forest model.

    Example:
        >>> data = pd.DataFrame({'Close': [1, 2, 3, 4, 5]})
        >>> model = train_random_forest(data, target='Close', window=2)
        >>> isinstance(model, RandomForestRegressor)
        True
    """
    X, y = prepare_data(data, target=target, window=window)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0
    )
    model = RandomForestRegressor()
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the performance of a machine learning model.

    Args:
        model: The trained machine learning model.
        X_test: The test features.
        y_test: The test target variable.

    Returns:
        float: The mean squared error of the model.

    Example:
        >>> model = RandomForestRegressor()
        >>> X_test = np.array([[1, 2], [2, 3]])
        >>> y_test = np.array([0, 1])
        >>> model.fit(X_test, y_test)
        RandomForestRegressor()
        >>> mse = evaluate_model(model, X_test, y_test)
        >>> isinstance(mse, float)
        True
    """
    y_pred = model.predict(X_test)
    return mean_squared_error(y_test, y_pred)
