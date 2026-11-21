"""Simulated (paper) trading portfolio (SPEC §5).

Executes buys, sells, and shorts at fetched daily prices and tracks cash,
positions, realized/unrealized P&L, and drawdown over time.
"""

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from kipvest import config
from kipvest.pipeline import Decision


@dataclass
class Position:
    ticker: str
    quantity: float  # negative for short positions
    avg_price: float


@dataclass(frozen=True)
class Trade:
    day: date
    ticker: str
    quantity: float  # positive = buy, negative = sell/short
    price: float


@dataclass
class Portfolio:
    cash: float = config.STARTING_CAPITAL
    positions: dict[str, Position] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)
    realized_pnl: float = 0.0
    equity_history: dict[date, float] = field(default_factory=dict)

    def buy(self, day: date, ticker: str, amount: float, price: float) -> Trade:
        """Buy ``amount`` of capital worth of ``ticker`` (or cover a short)."""
        raise NotImplementedError

    def sell(self, day: date, ticker: str, amount: float, price: float) -> Trade:
        """Sell ``amount`` of capital worth of ``ticker``, shorting if not held."""
        raise NotImplementedError

    def execute(self, day: date, decisions: list[Decision], prices: pd.Series) -> list[Trade]:
        """Apply the day's decisions at ``prices`` (ticker -> execution price)."""
        raise NotImplementedError

    def unrealized_pnl(self, prices: pd.Series) -> float:
        """Return open-position P&L marked at ``prices``."""
        raise NotImplementedError

    def equity(self, prices: pd.Series) -> float:
        """Return total portfolio value (cash + marked positions)."""
        raise NotImplementedError

    def mark_to_market(self, day: date, prices: pd.Series) -> float:
        """Record and return the portfolio equity for ``day``."""
        raise NotImplementedError

    def max_drawdown(self) -> float:
        """Return the max peak-to-trough drawdown of recorded equity."""
        raise NotImplementedError
