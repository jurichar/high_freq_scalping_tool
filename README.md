# Algo Day Trading Bot

Un bot de trading algorithmique pour le day trading avec des modèles prédictifs et des stratégies basées sur des indicateurs techniques. Ce projet utilise `yfinance` pour récupérer les données, `scikit-learn` et `TensorFlow` pour les prédictions, et `Flask` pour exposer une API RESTful.

## 📚 Table des Matières

- [Technologies](#technologies)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Fonctionnalités](#fonctionnalités)
- [Structure du Projet](#structure-du-projet)
- [Contribuer](#contribuer)
- [Licence](#licence)

## 🚀 Technologies

- Python 3.10+
- Flask
- yfinance
- scikit-learn
- TensorFlow / PyTorch
- pandas, NumPy
- ccxt, alpaca-trade-api
- Docker

## 📦 Installation

Clonez le dépôt :

```bash
git clone https://github.com/ton_nom_utilisateur/algo_day_trading.git
cd algo_day_trading
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Copiez le fichier env.example en .env et configurez vos variables d’environnement :

```bash
cp env.example .env
```

Assurez-vous de renseigner vos clés API pour les services de données et de trading.

## 🏃 Usage

Pour lancer le bot en local :

```bash
python main.py
```

Accédez à l’API sur `http://localhost:5000`

## 🔍 Fonctionnalités

- Récupération des données de marché via yfinance.
- Prédictions de prix à N+1 (par exemple, 5 minutes) avec scikit-learn et TensorFlow.
- Exécution automatisée des transactions.
- Interface RESTful avec Flask.
- Analyse des performances et reporting.

## 📂 Structure du Projet

Consultez la structure complète dans le fichier tree.txt.

## 🤝 Contribuer

Les contributions sont les bienvenues. Veuillez consulter les issues ouvertes et soumettre une pull request pour proposer vos améliorations.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
