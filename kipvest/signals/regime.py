"""Volatility & Regime filter (SPEC §3.3).

Classifies the market as Trending / Low-Volatility or Sideways /
High-Volatility relative to a broad benchmark, and supplies the
corresponding strategy weights.
"""

from enum import Enum

import pandas as pd

from kipvest import config


class Regime(Enum):
    TRENDING_LOW_VOL = "trending_low_vol"
    SIDEWAYS_HIGH_VOL = "sideways_high_vol"


# (w_trend, w_pairs) per regime — SPEC §4 Step 2.
REGIME_WEIGHTS: dict[Regime, tuple[float, float]] = {
    Regime.TRENDING_LOW_VOL: (0.70, 0.30),
    Regime.SIDEWAYS_HIGH_VOL: (0.30, 0.70),
}


def historical_volatility(
    close: pd.Series,
    window: int = config.VOLATILITY_WINDOW,
    periods_per_year: int = config.TRADING_DAYS_PER_YEAR,
) -> pd.Series:
    """Return rolling annualized standard deviation of daily returns."""
    raise NotImplementedError


def average_true_range(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = config.ATR_WINDOW,
) -> pd.Series:
    """Return the Average True Range."""
    raise NotImplementedError


def classify_regime(benchmark_close: pd.Series) -> Regime:
    """Classify the current market regime from benchmark price history."""
    raise NotImplementedError


def regime_weights(regime: Regime) -> tuple[float, float]:
    """Return ``(w_trend, w_pairs)`` for ``regime``."""
    raise NotImplementedError
