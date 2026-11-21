"""Monte Carlo risk estimation & position sizing (SPEC §3.4).

Simulates Geometric Brownian Motion paths from historical drift and
volatility to estimate tail risk. Used for sizing only — never direction.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from kipvest import config


@dataclass(frozen=True)
class RiskMetrics:
    """Simulated downside risk over the horizon, as positive loss fractions."""

    var: float  # e.g. 0.15 = 15% loss at the VaR confidence level
    expected_max_drawdown: float
    horizon_days: int


def estimate_gbm_params(close: pd.Series) -> tuple[float, float]:
    """Estimate daily ``(drift, volatility)`` from log returns of ``close``."""
    raise NotImplementedError


def simulate_gbm_paths(
    s0: float,
    mu: float,
    sigma: float,
    horizon_days: int = config.MC_HORIZON_DAYS,
    n_paths: int = config.MC_PATHS,
    seed: int | None = None,
) -> np.ndarray:
    """Return simulated prices of shape ``(n_paths, horizon_days + 1)``."""
    raise NotImplementedError


def value_at_risk(paths: np.ndarray, confidence: float = config.VAR_CONFIDENCE) -> float:
    """Return the loss fraction at ``confidence`` from terminal path values."""
    raise NotImplementedError


def expected_max_drawdown(paths: np.ndarray) -> float:
    """Return the mean of each path's maximum peak-to-trough drawdown."""
    raise NotImplementedError


def assess_risk(close: pd.Series, horizon_days: int = config.MC_HORIZON_DAYS) -> RiskMetrics:
    """Run the full simulation for one asset and return its ``RiskMetrics``."""
    raise NotImplementedError


def position_size_cap(score: float, risk: RiskMetrics, available_capital: float) -> float:
    """Return the max capital to allocate given conviction and tail risk.

    Higher simulated downside yields a tighter cap, even at high conviction.
    """
    raise NotImplementedError
