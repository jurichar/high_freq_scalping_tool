# Algo Day Trading Bot

An algorithmic trading bot for day trading with predictive models and strategies based on technical indicators. This project uses `yfinance` to fetch data, `scikit-learn` and `TensorFlow` for predictions, and `Flask` to expose a RESTful API.

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

Access the API at `http://localhost:5000`.

## 🔍 Functionalities

- Fetching historical data and technical indicators.
- Predicting price at N+1 (e.g., 5 minutes) with scikit-learn and TensorFlow.
- Automated trading execution.
- Back-end api with Flask.
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

## 🤝 Contribute

The project is open to contributions. Feel free to open an issue or submit a pull request.
