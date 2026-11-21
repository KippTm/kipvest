# Kipvest

A personal quantitative analysis and simulated trading suite. Kipvest fetches daily opening and closing stock prices via `yfinance`, evaluates directional and relative-value signals under a regime-aware weighting scheme, sizes positions using Monte Carlo risk budgeting, and simulates portfolio trades.

If it works well, then I'm my own mini quant firm :)

## Architecture Overview

Kipvest is organized around four core analytical modules feeding a unified daily decision pipeline:

1. **Trend / Momentum (Directional Signal)** — Dual EMA crossover (20-day vs. 50-day) paired with an RSI or ROC momentum filter.
2. **Mean Reversion / Pairs Trading (Relative Value Signal)** — Engle-Granger cointegration for pair discovery with spread Z-score signals at `±2` standard deviations.
3. **Volatility & Regime Filter (Market Context)** — Rolling historical volatility or ATR compared against a broad benchmark (e.g., S&P 500 or OMX C25) to classify *Trending / Low-Volatility* vs. *Sideways / High-Volatility* regimes.
4. **Monte Carlo Simulation (Risk & Position Sizing)** — 1,000-path Geometric Brownian Motion (GBM) simulations over 5-day or 20-day horizons to estimate VaR and expected maximum drawdown for capital allocation.

All directional signals are normalized to `[-1.0, +1.0]`, combined using regime-dependent weights (`70/30` or `30/70`), filtered through a `[-0.4, +0.4]` hold dead-zone, and sized according to Monte Carlo tail risk before simulating trades.

## Documentation

- **[Technical Specification](DOCS/SPEC.md)** — Detailed module specifications, scoring math, weighting tables, and pipeline rules.
- **[Project Context & Design Rationale](DOCS/CONTEXTS.md)** — Architectural reasoning, domain glossary, assumptions, and boundaries.

## Project Structure

```text
stonks/
├── DOCS/
│   ├── CONTEXTS.md      # Domain context, design rationale, and glossary
│   └── SPEC.md          # Detailed technical specification
├── fetcher.py           # Daily stock price fetcher (yfinance)
├── requirements.txt     # Python dependencies
├── README.md
└── stonkenv/            # Local Python virtual environment
```

## Setup

Activate the virtual environment and install dependencies:

```bash
source stonkenv/bin/activate
pip install -r requirements.txt
```
