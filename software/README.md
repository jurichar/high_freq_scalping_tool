# Plan

1. Analyse des marchés:
   - Récupérer les data actuelles du marché (prix, volume, volatilité, etc.). (data_collector + data_processor)
   - Analyser les indicateurs techniques (Moyenne mobile, RSI, MACD, etc.). (jupyter notebook)
   - Évaluer les fondamentaux de l'actif (nouvelles, annonces économiques, etc.).
   - Calculer la probabilité d'un mouvement de marché basé sur l'analyse quantitative. (strategy)

2. Définir les objectifs et contraintes:
   - Fixer ProfitTarget & StopLoss via l'ATR.'
   - Déterminer la taille de la position basée sur le capital alloué (RiskPerTrade). (calculate_size)

3. Calcul du risque et positionnement:
   - Récupérer le prix actuel de l'actif (CurrentPrice).
   <!-- - Calculer la volatilité du marché ou de l'actif pour ajuster le risque. -->
   - Utiliser la formule suivante pour la taille de la position:

     ```bash
     PositionSize = Capital * RiskPerTrade / (CurrentPrice - StopLoss)
     ```

     Où:
     - Capital = capital total alloué.
     - RiskPerTrade = pourcentage du capital alloué pour le risque sur cette position.
     - StopLoss = niveau de prix auquel la position sera fermée si elle atteint ce niveau.

4. Exécution de la position:
   - Vérifier la liquidité de l'actif avant d'exécuter l'ordre.
   - Placer l'ordre d'achat ou de vente au prix souhaité (MarketOrder ou LimitOrder).
   - Enregistrer la position (prix d'entrée, taille de la position, date et heure).

5. Gestion de la position:
   - Suivre en temps réel l'évolution du prix.
   - Ajuster le StopLoss en fonction de la volatilité ou des événements du marché.
   - Si le prix atteint l'objectif de profit, clôturer la position.
   - Si le prix atteint le StopLoss, clôturer automatiquement pour limiter les pertes.

6. Clôture de la position:
   - Calculer le profit ou la perte réalisée (PnL):

     ```bash
     PnL = (Prix de clôture - Prix d'entrée) * PositionSize
     ```

   - Consigner les résultats dans le journal de trading pour analyse ultérieure.










Actions : Unité = 1 Action.
i.e. 1 Action de Tesla, 1 Action de Apple, etc.

Fraction d'actions : Unité = 0.1 Action.
i.e. 0.1 Action de Tesla, 0.1 Action de Apple, etc.

Indices : Unité = 1 Contrat dérivé.
i.e. 1 Contrat de S&P 500, 1 Contrat de Nasdaq 100, etc.

Contrat dérivé : Instrument financier dont la valeur dépend de l'évolution d'un actif sous-jacent.
i.e. Futures, CFD, Options, etc.

Contracts for Difference (CFD) : Contrat entre deux parties pour échanger la différence entre le prix d'ouverture et de clôture d'un contrat.
i.e. CFD sur Actions, CFD sur Indices, CFD sur Matières premières, etc.

Futures : Contrat à terme standardisé négocié sur une bourse pour acheter ou vendre un actif sous-jacent à une date future prédéterminée.
i.e. Futures sur Actions, Futures sur Indices, Futures sur Matières premières, etc.

Sous-jacent : Actif financier sur lequel est basé un contrat dérivé (actions, indices, matières premières, devises, etc.).
i.e. Actions, Indices, Matières premières, Devises, etc.
