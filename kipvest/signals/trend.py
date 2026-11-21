"""Trend / Momentum directional signal (SPEC §3.1).

Dual EMA crossover (fast vs. slow) combined with an RSI or ROC momentum
filter, producing a normalized directional score in ``[-1.0, +1.0]``.
"""

import pandas as pd

from kipvest import config


def compute_ema(prices: pd.Series, span: int) -> pd.Series:
    """Return the exponential moving average of ``prices`` over ``span`` days."""
    raise NotImplementedError


def ema_crossover(
    prices: pd.Series,
    fast: int = config.EMA_FAST,
    slow: int = config.EMA_SLOW,
) -> pd.Series:
    """Return the fast-minus-slow EMA spread (positive = uptrend)."""
    raise NotImplementedError


def compute_rsi(prices: pd.Series, window: int = config.RSI_WINDOW) -> pd.Series:
    """Return the Relative Strength Index (0-100) of ``prices``."""
    raise NotImplementedError


def compute_roc(prices: pd.Series, window: int = config.ROC_WINDOW) -> pd.Series:
    """Return the Rate of Change (percent) of ``prices`` over ``window`` days."""
    raise NotImplementedError


def trend_score(close: pd.Series) -> float:
    """Return the latest directional score for one asset in ``[-1.0, +1.0]``.

    Combines EMA crossover direction/strength with the momentum filter to
    dampen overextended moves.
    """
    raise NotImplementedError


def trend_scores(closes: pd.DataFrame) -> pd.Series:
    """Return the latest trend score for every ticker (column) in ``closes``."""
    raise NotImplementedError
