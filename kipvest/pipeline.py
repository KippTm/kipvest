"""Signal aggregation & daily decision pipeline (SPEC §4).

Per ticker: combine trend and pairs scores with regime weights, apply the
dead-zone threshold, and size actionable signals with Monte Carlo risk.
"""

from dataclasses import dataclass
from enum import Enum

import pandas as pd

from kipvest import config
from kipvest.signals.regime import Regime


class Action(Enum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"  # short / sell


@dataclass(frozen=True)
class Decision:
    ticker: str
    trend_score: float
    pairs_score: float
    combined_score: float
    action: Action
    allocation: float  # capital to commit; 0.0 for HOLD


def combine_scores(trend_score: float, pairs_score: float, regime: Regime) -> float:
    """Return ``w_trend * trend_score + w_pairs * pairs_score`` (Step 2)."""
    raise NotImplementedError


def decide_action(combined_score: float, dead_zone: float = config.DEAD_ZONE) -> Action:
    """Map a combined score to an ``Action`` via the dead-zone buffer (Step 3)."""
    raise NotImplementedError


def run_daily_pipeline(
    prices: pd.DataFrame,
    benchmark_close: pd.Series,
    available_capital: float,
) -> list[Decision]:
    """Run Steps 1-4 for every ticker and return the day's decisions.

    Args:
        prices: ``fetcher.batch_download`` output for tracked tickers.
        benchmark_close: Benchmark closing prices for regime classification.
        available_capital: Cash available for new positions.
    """
    raise NotImplementedError
