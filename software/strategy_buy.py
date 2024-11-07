import numpy as np
import pandas as pd


class Strategy:
    def __init__(
        self,
        ema_sma_threshold=0,
        rsi_long_threshold=30,
        rsi_short_threshold=70,
        bb_threshold=0,
    ):
        self.ema_sma_threshold = ema_sma_threshold
        self.rsi_long_threshold = rsi_long_threshold
        self.rsi_short_threshold = rsi_short_threshold
        self.bb_threshold = bb_threshold

    def generate_buy_long_signals(self, data):
        """
        Generates buy signals for long positions based on precomputed EMA crossover, RSI, and Bollinger Bands.

        Args:
            data (pd.DataFrame): Stock data with precomputed technical indicators.

        Returns:
            pd.Series: Series with buy signals for long positions.

        Example:
            >>> strategy = Strategy()
            >>> data = pd.DataFrame({
            ...     'Close': [10, 20, 30, 40, 50],
            ...     'SMA': [15, 25, 35, 45, 55],
            ...     'EMA': [12, 22, 32, 42, 52],
            ...     'RSI': [20, 30, 40, 50, 60],
            ...     'BollingerB_Lower': [10, 20, 30, 40, 50],
            ...     'BollingerB_Upper': [20, 30, 40, 50, 60],
            ... })
            >>> strategy.generate_buy_long_signals(data=data)
            [False, False, False, False, False]

            >>> data = pd.DataFrame({
            ...     'Close': [10, 15, 20, 25, 30],
            ...     'SMA': [20, 25, 30, 35, 40],
            ...     'EMA': [18, 22, 28, 32, 38],
            ...     'RSI': [25, 28, 35, 40, 42],
            ...     'BollingerB_Lower': [12, 18, 25, 30, 35],
            ...     'BollingerB_Upper': [22, 28, 35, 40, 45],
            ... })
            >>> strategy.generate_buy_long_signals(data=data)
            [True, True, False, False, False]
        """

        ema_signal = np.where(
            data["EMA"] > (data["SMA"] + self.ema_sma_threshold), 1, 0
        )
        rsi_signal = np.where(data["RSI"] < self.rsi_long_threshold, 1, 0)
        bb_signal = np.where(
            data["Close"] < (data["BollingerB_Lower"] - self.bb_threshold),
            1,
            0,
        )

        final_signal = (ema_signal + rsi_signal + bb_signal) > 1
        return final_signal.tolist()

    def generate_buy_short_signals(self, data):
        """
        Generates buy signals for short positions based on precomputed EMA crossover, RSI, and Bollinger Bands.

        Args:
            data (pd.DataFrame): Stock data with precomputed technical indicators.

        Returns:
            pd.Series: Series with buy signals for short positions.

        Example:
            >>> strategy = Strategy()
            >>> data = pd.DataFrame({
            ...     'Close': [10, 20, 30, 40, 50],
            ...     'SMA': [15, 25, 35, 45, 55],
            ...     'EMA': [12, 22, 32, 42, 52],
            ...     'RSI': [20, 30, 40, 50, 60],
            ...     'BollingerB_Lower': [10, 20, 30, 40, 50],
            ...     'BollingerB_Upper': [20, 30, 40, 50, 60],
            ... })
            >>> strategy.generate_buy_short_signals(data)
            [False, False, False, False, False]

            >>> data = pd.DataFrame({
            ...     'Close': [55, 60, 65, 70, 75],
            ...     'SMA': [50, 55, 60, 65, 70],
            ...     'EMA': [52, 57, 62, 67, 72],
            ...     'RSI': [75, 72, 71, 68, 67],
            ...     'BollingerB_Lower': [45, 50, 55, 60, 65],
            ...     'BollingerB_Upper': [55, 60, 65, 70, 75],
            ... })
            >>> strategy.generate_buy_short_signals(data)
            [True, True, True, False, False]

        """
        ema_signal = np.where(
            data["EMA"] < (data["SMA"] - self.ema_sma_threshold), 1, 0
        )
        rsi_signal = np.where(data["RSI"] > self.rsi_short_threshold, 1, 0)
        bb_signal = np.where(
            data["Close"] >= (data["BollingerB_Upper"] + self.bb_threshold),
            1,
            0,
        )

        final_signal = (ema_signal + rsi_signal + bb_signal) > 1

        return final_signal.tolist()

    def generate_buy_signals(self, data):
        """
        Generate buy signals based on precomputed technical indicators.

        Args:
            data (pd.DataFrame): Stock data with precomputed technical indicators.

        Returns:
            pd.DataFrame: DataFrame with buy/sell signals.

        Example:
            >>> strategy = Strategy()
            >>> data = pd.DataFrame({
            ...     'Close': [10, 20, 30, 40, 50],
            ...     'SMA': [15, 25, 35, 45, 55],
            ...     'EMA': [12, 22, 32, 42, 52],
            ...     'RSI': [20, 30, 40, 50, 60],
            ...     'BollingerB_Lower': [10, 20, 30, 40, 50],
            ...     'BollingerB_Upper': [20, 30, 40, 50, 60],
            ... })
            >>> strategy.generate_buy_signals(data).Signal.tolist()
            [0, 0, 0, 0, 0]

            >>> data = pd.DataFrame({
            ...     'Close': [55, 60, 65, 70, 75, 10, 15, 20, 25, 30],
            ...     'SMA': [50, 55, 60, 65, 70, 20, 25, 30, 35, 40],
            ...     'EMA': [52, 57, 62, 67, 72, 18, 22, 28, 32, 38],
            ...     'RSI': [75, 72, 71, 68, 67, 25, 28, 35, 40, 42],
            ...     'BollingerB_Lower': [45, 50, 55, 60, 65, 12, 18, 25, 30, 35],
            ...     'BollingerB_Upper': [55, 60, 65, 70, 75, 22, 28, 35, 40, 45],
            ... })
            >>> strategy.generate_buy_signals(data).Signal.tolist()
            [-1, -1, -1, 0, 0, 1, 1, 0, 0, 0]

        """
        buy_short_signal = self.generate_buy_short_signals(data)
        buy_long_signal = self.generate_buy_long_signals(data)

        final_signal = np.where(buy_short_signal, -1, 0)
        final_signal = np.where(buy_long_signal, 1, final_signal)

        data["Signal"] = final_signal
        return data
