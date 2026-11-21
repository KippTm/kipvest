# Kipvest — Project Context & Design Rationale

## 1. Vision & Motivation

**Kipvest** is a personal quantitative trading research and paper-trading suite ("my own mini quant firm"). Its goal is to retrieve stock prices daily, run a structured set of quantitative models, and simulate portfolio trades based on those calculations to evaluate strategy performance before risking real capital.

---

## 2. Design Rationale & Mental Models

### Why Cointegration Instead of Correlation for Pairs Trading?
Simple price correlation can be spurious—two trending stocks may show high correlation while steadily drifting apart. Using the **Engle-Granger cointegration test** ensures that candidate pairs share a statistically stationary long-term equilibrium spread, making mean-reversion bets around `±2` standard deviations mathematically grounded.

### Why Regime-Aware Weighting Instead of Static 50/50 Weights?
Trend-following and mean-reversion strategies have opposing failure modes:
- **Mean reversion gets crushed** when an asset enters a sustained breakout.
- **Trend-following gets whipsawed** by false breakouts in sideways, choppy markets.

Dynamically shifting weights (`70/30` vs. `30/70`) based on the Volatility & Regime Filter allows the suite to lean into the strategy best suited to current market conditions.

### Why Monte Carlo Is Used for Risk Sizing—Not Direction
Standard Geometric Brownian Motion (GBM) simulates random walks parameterized by historical drift and volatility. Because future returns are not reliably predictable from historical drift alone, GBM cannot tell you whether a stock will go up or down next week. Instead, it is well-suited for **risk budgeting**: estimating tail risk (VaR and expected maximum drawdown) over a 5-day or 20-day window so high-conviction signals on volatile stocks are sized conservatively.

### Why a Dead-Zone Buffer (`[-0.4, +0.4]`)?
Acting on every marginal non-zero score leads to frequent small trades, whipsaw losses, and unnecessary fee drag. The dead-zone threshold forces the simulator to hold unless combined conviction is meaningful.

### Market & Benchmark Context
The suite references both **S&P 500** and **OMX C25** as candidate broad market benchmarks, indicating potential coverage of both US and Danish/Nordic equities. Implementations should remain ticker-agnostic and support standard Yahoo Finance ticker symbols (including exchange suffixes such as `.CO` for Copenhagen-listed equities).

---

## 3. Operational Context & Boundaries

- **Data Source**: Daily stock data (opening and closing prices, plus high/low when required for indicators like ATR) fetched via `yfinance`.
- **Cadence**: Daily end-of-day / daily-bar processing. High-frequency or intraday execution is out of scope.
- **Execution Mode**: Simulated trading (paper trading) only. No live brokerage API integration or real-money order routing.
- **Runtime Environment**: Local Python environment (`stonkenv` virtual environment in the repository root).

---

## 4. Domain Glossary

| Term | Meaning in Kipvest |
| :--- | :--- |
| **EMA (20/50)** | 20-day and 50-day Exponential Moving Averages used to detect directional trend crossovers. |
| **RSI / ROC** | Relative Strength Index / Rate of Change; momentum filters to identify trend strength and overextension. |
| **Engle-Granger Test** | Statistical test for cointegration between two price series to identify valid trading pairs. |
| **Spread Z-Score** | Number of standard deviations a pair's current price spread deviates from its rolling mean. |
| **ATR** | Average True Range; a volatility indicator measuring typical daily price range. |
| **Market Regime** | Broad market state classified as either *Trending / Low-Volatility* or *Sideways / High-Volatility*. |
| **GBM** | Geometric Brownian Motion; stochastic process used in Monte Carlo path simulations. |
| **VaR** | Value at Risk; estimated worst-case loss at a given confidence level over a set horizon. |
| **Unified Score** | Normalized signal output on `[-1.0, +1.0]` allowing heterogeneous models to be combined. |
