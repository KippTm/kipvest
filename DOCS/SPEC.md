# Kipvest — Technical Specification

## 1. Overview

**Kipvest** is a daily quantitative analysis and simulated trading suite. On a daily cadence, it fetches market data via `yfinance`, computes directional and relative-value signals, classifies the prevailing market regime, sizes positions using Monte Carlo risk budgeting, and simulates trade execution against a virtual portfolio.

---

## 2. Data Ingestion

- **Source**: `yfinance` (implemented in `fetcher.py`).
- **Cadence**: Daily.
- **Tracked Data**:
  - Daily **Opening** and **Closing** prices for all tracked equities (plus High/Low where required by volatility indicators such as ATR).
  - Daily benchmark index data (e.g., S&P 500 `^GSPC` or OMX C25 `^OMXC25`) for market regime classification.
- **Historical Lookback**: Sufficient rolling history must be retained/fetched to support indicator warm-up windows (e.g., 50+ trading days for the slow EMA, and longer windows for cointegration testing).

---

## 3. Analytical Modules

### 3.1 Trend / Momentum (Directional Signal)
Determines whether an asset is trending up or down and whether the move is overextended.

- **Trend Indicator**: Dual Exponential Moving Average (EMA) crossover (default: 20-day fast EMA vs. 50-day slow EMA).
- **Momentum Filter**: Relative Strength Index (RSI) or Rate of Change (ROC) to gauge trend strength and overextension.
- **Output**: Continuous normalized directional score in `[-1.0, +1.0]`.

### 3.2 Mean Reversion / Pairs Trading (Relative Value Signal)
Identifies temporary divergences between historically linked equities and bets on spread convergence.

- **Pair Identification**: Cointegration testing via the **Engle-Granger** two-step test (rather than simple price correlation) to select stock pairs that share a long-term equilibrium relationship.
- **Spread Tracking**: Compute the rolling Z-score of the pair's price spread.
- **Signal Logic**:
  - When the spread Z-score stretches past `±2.0` standard deviations, generate opposing signals: buy the underperformer and short the outperformer.
  - Example: If a pair's spread Z-score is `+2.0`, the long leg receives `+1.0` and the short leg receives `-1.0`.
- **Output**: Continuous normalized relative-value score in `[-1.0, +1.0]`.

### 3.3 Volatility & Regime Filter (Market Context)
Classifies the current market environment to dynamically adjust strategy weights.

- **Volatility Metric**: Rolling historical volatility (e.g., 20-day annualized standard deviation of returns) or Average True Range (ATR).
- **Benchmark Comparison**: Compare asset/market volatility and trend characteristics against a broad market benchmark (e.g., S&P 500 or OMX C25).
- **Regime Classification**:
  - **Trending / Low-Volatility**
  - **Sideways / High-Volatility**

### 3.4 Monte Carlo Simulation (Risk & Position Sizing)
Estimates short-term downside risk for position sizing. **Not used for directional forecasting.**

- **Model**: Geometric Brownian Motion (GBM) parameterized by historical drift and volatility.
- **Simulation Parameters**: `1,000` simulated price paths over a `5-day` or `20-day` horizon.
- **Risk Metrics**:
  - **Value at Risk (VaR)** (e.g., 5% tail loss over the simulation horizon).
  - **Expected Maximum Drawdown**.
- **Output**: Risk budget / position-size cap per candidate trade.

---

## 4. Signal Aggregation & Decision Pipeline

Each trading day, the suite executes the following four-step pipeline per tracked stock:

### Step 1: Normalize to a Unified Score (`[-1.0, +1.0]`)
Convert every directional and relative-value model output into a continuous score:
- `+1.0`: Maximum conviction Long / Buy
- `0.0`: Neutral / Hold
- `-1.0`: Maximum conviction Short / Sell

### Step 2: Regime-Aware Weighting
Combine the Trend/Momentum score ($S_{\text{trend}}$) and Pairs/Mean Reversion score ($S_{\text{pairs}}$) using weights supplied by the Volatility & Regime Filter:

| Market Regime | Trend Weight ($w_{\text{trend}}$) | Pairs / Mean Reversion Weight ($w_{\text{pairs}}$) |
| :--- | :---: | :---: |
| **Trending / Low-Volatility** | `0.70` (70%) | `0.30` (30%) |
| **Sideways / High-Volatility** | `0.30` (30%) | `0.70` (70%) |

$$S_{\text{combined}} = w_{\text{trend}} \cdot S_{\text{trend}} + w_{\text{pairs}} \cdot S_{\text{pairs}}$$

### Step 3: Action Thresholding (Dead-Zone Buffer)
Apply a dead-zone buffer around `0.0` to prevent excessive turnover and simulated fee drag on weak signals:

| Combined Score | Action |
| :--- | :--- |
| $S_{\text{combined}} > +0.4$ | **Buy** |
| $-0.4 \le S_{\text{combined}} \le +0.4$ | **Hold** |
| $S_{\text{combined}} < -0.4$ | **Short / Sell** |

### Step 4: Monte Carlo Position Sizing
For every actionable signal (Buy or Short/Sell), allocate capital from the portfolio's starting/available sum based on both signal conviction and Monte Carlo tail risk:
- Trades with higher simulated downside risk (e.g., a 5% chance of a 15% drop over the next 5 days) receive a tighter position-size cap than trades with lower simulated tail risk, even if their conviction score is high (e.g., `+0.8`).

---

## 5. Trade Simulation

- Executes simulated buys, sells, and shorts using fetched daily opening/closing prices.
- Tracks virtual cash balance, open positions, position sizes, realized/unrealized P&L, and portfolio drawdown over time.
