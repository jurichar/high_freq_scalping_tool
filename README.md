# High-Frequency Scalping Tool

A high-frequency trading bot for day trading with predictive models (TBD) and strategies based on technical indicators.
This project has the goal to provide a framework for developing and testing day trading strategies with a focus on scalping.

## 📚 Table des Matières

- [Technologies](#-technologies)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Functionalities](#-functionalities)
- [Tests](#-tests)
- [Contribute](#-contribute)

## 🚀 Technologies

- yfinance
- pandas
- scikit-learn
- TensorFlow / PyTorch
- ccxt, alpaca-trade-api
- matplotlib
- jupyter

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/jurichar/algo_day_trading.git
cd algo_day_trading
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Copy the env.example file to .env and configure your environment variables:

```bash
cp env.example .env
```

Make sure to fill in your API keys for data and trading services.

## 🏃 Usage

To start the bot, run:

```bash
python main.py
```

or start the jupyter notebook:

```bash
jupyter notebook
```

## 🔍 Functionalities

- Fetching historical data and technical indicators.
- Tests and coverage with pytest.
- Visualizing data and technical indicator with Matplotlib and Jupyter.
- Trading operations like buy, sell, TP, SL, leverage, etc.
- Backtesting framework.
- Performance analysis and reporting.

## 🧪 Tests

To execute the tests, run:

```bash
pytest
```

or with only a specific test file:

```bash
pytest --doctest-modules my_file.py
```

With coverage:

```bash
pytest --cov=./
```

## 🤝 Contribute

The project is open to contributions. Feel free to open an issue or submit a pull request.
