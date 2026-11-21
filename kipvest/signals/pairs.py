"""Mean Reversion / Pairs Trading relative-value signal (SPEC §3.2).

Pairs are discovered with the Engle-Granger cointegration test. The rolling
Z-score of each pair's spread drives opposing long/short scores in
``[-1.0, +1.0]``.
"""

from dataclasses import dataclass

import pandas as pd

from kipvest import config


@dataclass(frozen=True)
class Pair:
    """A cointegrated pair: ``spread = y - hedge_ratio * x``."""

    y: str
    x: str
    hedge_ratio: float
    pvalue: float


def engle_granger_test(y: pd.Series, x: pd.Series) -> tuple[float, float]:
    """Run the Engle-Granger two-step test.

    Returns:
        ``(pvalue, hedge_ratio)``.
    """
    raise NotImplementedError


def find_cointegrated_pairs(
    closes: pd.DataFrame,
    pvalue_threshold: float = config.COINTEGRATION_PVALUE,
) -> list[Pair]:
    """Test every ticker combination in ``closes`` and return cointegrated pairs."""
    raise NotImplementedError


def compute_spread(y: pd.Series, x: pd.Series, hedge_ratio: float) -> pd.Series:
    """Return the pair spread ``y - hedge_ratio * x``."""
    raise NotImplementedError


def spread_zscore(spread: pd.Series, window: int = config.ZSCORE_WINDOW) -> pd.Series:
    """Return the rolling Z-score of ``spread``."""
    raise NotImplementedError


def pair_scores(zscore: float, entry: float = config.ZSCORE_ENTRY) -> tuple[float, float]:
    """Map a spread Z-score to ``(y_score, x_score)`` in ``[-1.0, +1.0]``.

    Beyond ``±entry`` the underperformer is scored long and the outperformer
    short, e.g. Z = +2.0 -> y short (-1.0), x long (+1.0).
    """
    raise NotImplementedError


def pairs_scores(closes: pd.DataFrame, pairs: list[Pair]) -> pd.Series:
    """Return the latest relative-value score per ticker across all ``pairs``.

    Tickers not in any active pair score ``0.0``.
    """
    raise NotImplementedError
