"""Fetch daily stock prices from Yahoo Finance via ``yfinance``.

All download functions return data in a consistent "wide" layout:

* ``batch_download`` returns a DataFrame indexed by date with two-level
  columns ``(field, ticker)``, e.g. ``("Close", "AAPL")``.
* ``get_opening_prices`` / ``get_closing_prices`` return a DataFrame indexed
  by date with one column per ticker.

Tickers use standard Yahoo Finance symbols, including exchange suffixes
(e.g. ``NOVO-B.CO`` for Copenhagen) and index symbols (e.g. ``^GSPC``).

When tickers from different exchanges are mixed, the date index is the union
of all trading days, so a ticker has NaN on days its exchange was closed.
"""

import logging
import time
from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

PRICE_FIELDS = ("Open", "High", "Low", "Close", "Volume")
DEFAULT_PERIOD = "1y"
DEFAULT_BATCH_SIZE = 50
DEFAULT_PAUSE_SECONDS = 1.0
DEFAULT_PRICES_PATH = Path("data/prices.csv")

TickerInput = str | Iterable[str]


def _normalize_tickers(tickers: TickerInput) -> list[str]:
    """Return a de-duplicated, order-preserving list of cleaned ticker symbols.

    Accepts a single symbol, a whitespace/comma separated string, or an
    iterable of symbols.
    """
    if isinstance(tickers, str):
        tickers = tickers.replace(",", " ").split()
    cleaned = (t.strip().upper() for t in tickers if t and t.strip())
    result = list(dict.fromkeys(cleaned))
    if not result:
        raise ValueError("At least one ticker symbol is required.")
    return result


def _chunk(items: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _download_chunk(
    tickers: list[str],
    start: str | None,
    end: str | None,
    period: str | None,
    interval: str,
    auto_adjust: bool,
) -> pd.DataFrame:
    """Download a single chunk of tickers with a ``(field, ticker)`` column layout."""
    data = yf.download(
        tickers,
        start=start,
        end=end,
        # yfinance ignores ``period`` when ``start`` is given.
        period=None if start else period,
        interval=interval,
        auto_adjust=auto_adjust,
        group_by="column",
        multi_level_index=True,
        threads=True,
        progress=False,
    )
    if data is None or data.empty:
        return pd.DataFrame()
    return data


def batch_download(
    tickers: TickerInput,
    start: str | None = None,
    end: str | None = None,
    period: str | None = DEFAULT_PERIOD,
    interval: str = "1d",
    auto_adjust: bool = True,
    batch_size: int = DEFAULT_BATCH_SIZE,
    pause: float = DEFAULT_PAUSE_SECONDS,
) -> pd.DataFrame:
    """Download OHLCV price history for many tickers, in batches.

    Large ticker lists are split into chunks of ``batch_size`` to avoid
    Yahoo rate limiting; ``pause`` seconds are slept between chunks.

    Args:
        tickers: Ticker symbol(s), e.g. ``["AAPL", "MSFT", "^GSPC"]``.
        start: Inclusive start date (``"YYYY-MM-DD"``). Overrides ``period``.
        end: Exclusive end date (``"YYYY-MM-DD"``). Defaults to today.
        period: Lookback window when ``start`` is not given (e.g. ``"6mo"``,
            ``"1y"``, ``"5y"``, ``"max"``).
        interval: Bar size. Kipvest operates on daily bars (``"1d"``).
        auto_adjust: Adjust prices for splits and dividends.
        batch_size: Maximum tickers per request.
        pause: Seconds to wait between batch requests.

    Returns:
        DataFrame indexed by date with ``(field, ticker)`` MultiIndex columns.
        Tickers that returned no data are dropped and logged as warnings.

    Raises:
        ValueError: If no tickers are given or ``batch_size`` < 1.
        RuntimeError: If no data could be downloaded for any ticker.
    """
    symbols = _normalize_tickers(tickers)
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1.")

    frames: list[pd.DataFrame] = []
    chunks = list(_chunk(symbols, batch_size))
    for i, chunk in enumerate(chunks):
        if i > 0 and pause > 0:
            time.sleep(pause)
        logger.info("Downloading batch %d/%d (%d tickers)", i + 1, len(chunks), len(chunk))
        frame = _download_chunk(chunk, start, end, period, interval, auto_adjust)
        if not frame.empty:
            frames.append(frame)

    if not frames:
        raise RuntimeError(f"No price data downloaded for: {', '.join(symbols)}")

    data = pd.concat(frames, axis=1).sort_index()
    data = data.loc[:, ~data.columns.duplicated()]

    # Drop tickers whose every value is missing (delisted / invalid symbols).
    has_data = data.notna().T.groupby(level=1).any().any(axis=1)
    missing = [t for t in symbols if not has_data.get(t, False)]
    if missing:
        logger.warning("No data returned for: %s", ", ".join(missing))
        data = data.drop(columns=missing, level=1, errors="ignore")

    if data.empty:
        raise RuntimeError(f"No price data downloaded for: {', '.join(symbols)}")

    data.columns = data.columns.remove_unused_levels()
    data.columns.names = ["Field", "Ticker"]
    return data


def get_price_field(field: str, source: pd.DataFrame | TickerInput, **download_kwargs) -> pd.DataFrame:
    """Return one price field (e.g. ``"Open"``) as a date x ticker DataFrame.

    Args:
        field: One of ``PRICE_FIELDS``.
        source: Either a DataFrame previously returned by ``batch_download``
            (no network call is made), or ticker symbol(s) to download.
        **download_kwargs: Passed to ``batch_download`` when ``source`` is
            ticker symbol(s), e.g. ``period="3mo"``.
    """
    if field not in PRICE_FIELDS:
        raise ValueError(f"Unknown field {field!r}; expected one of {PRICE_FIELDS}.")

    if isinstance(source, pd.DataFrame):
        if download_kwargs:
            raise TypeError("download_kwargs are only valid when downloading by ticker.")
        data = source
    else:
        data = batch_download(source, **download_kwargs)

    if field not in data.columns.get_level_values(0):
        raise KeyError(f"Field {field!r} not present in price data.")

    prices = data[field].copy()
    prices.columns.name = "Ticker"
    return prices


def get_opening_prices(source: pd.DataFrame | TickerInput, **download_kwargs) -> pd.DataFrame:
    """Return daily opening prices as a date x ticker DataFrame.

    ``source`` is a ``batch_download`` result or ticker symbol(s); see
    ``get_price_field``.
    """
    return get_price_field("Open", source, **download_kwargs)


def get_closing_prices(source: pd.DataFrame | TickerInput, **download_kwargs) -> pd.DataFrame:
    """Return daily closing prices as a date x ticker DataFrame.

    ``source`` is a ``batch_download`` result or ticker symbol(s); see
    ``get_price_field``.
    """
    return get_price_field("Close", source, **download_kwargs)


def to_long(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert a wide ``(Field, Ticker)`` DataFrame to long format.

    Returns one row per ``(Date, Ticker)`` with columns
    ``["Date", "Ticker", *fields]``, dropping rows where all price fields
    are missing.
    """
    if not isinstance(prices.columns, pd.MultiIndex) or prices.columns.nlevels != 2:
        raise ValueError("Expected a wide DataFrame with (Field, Ticker) MultiIndex columns.")

    stacked = prices.stack(level=1).dropna(how="all")
    stacked.index.names = ["Date", "Ticker"]
    long_df = stacked.reset_index()
    long_df["Date"] = pd.to_datetime(long_df["Date"]).dt.normalize()

    ordered_fields = [f for f in PRICE_FIELDS if f in long_df.columns]
    extra_fields = [c for c in long_df.columns if c not in ("Date", "Ticker", *ordered_fields)]
    return long_df[["Date", "Ticker", *ordered_fields, *extra_fields]]


def to_wide(long_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot a long ``(Date, Ticker, ...)`` DataFrame back to ``(Field, Ticker)``."""
    required = {"Date", "Ticker"}
    if not required.issubset(long_df.columns):
        raise ValueError("Expected columns 'Date' and 'Ticker' in long_df.")

    df = long_df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    value_cols = [f for f in PRICE_FIELDS if f in df.columns]
    if not value_cols:
        value_cols = [c for c in df.columns if c not in ("Date", "Ticker")]

    wide = df.pivot(index="Date", columns="Ticker", values=value_cols).sort_index()
    wide.columns.names = ["Field", "Ticker"]
    return wide


def save_prices(prices: pd.DataFrame, path: str | Path = DEFAULT_PRICES_PATH) -> Path:
    """Save or incrementally append ``prices`` to a long-format CSV file.

    Accepts either a wide ``batch_download`` DataFrame or an already-long
    DataFrame. Existing ``(Date, Ticker)`` rows are updated in place so
    re-running on the same day never creates duplicates.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    incoming = to_long(prices) if isinstance(prices.columns, pd.MultiIndex) else prices.copy()
    incoming["Date"] = pd.to_datetime(incoming["Date"]).dt.normalize()

    if target.exists():
        existing = pd.read_csv(target, parse_dates=["Date"])
        combined = pd.concat([existing, incoming], ignore_index=True)
    else:
        combined = incoming

    combined = (
        combined.drop_duplicates(subset=["Date", "Ticker"], keep="last")
        .sort_values(["Date", "Ticker"])
        .reset_index(drop=True)
    )
    combined.to_csv(target, index=False, date_format="%Y-%m-%d")
    return target


def load_prices(path: str | Path = DEFAULT_PRICES_PATH, wide: bool = True) -> pd.DataFrame:
    """Load saved prices from a long-format CSV file.

    Returns a wide ``(Field, Ticker)`` DataFrame by default (matching
    ``batch_download``), or the raw long DataFrame when ``wide=False``.
    """
    df = pd.read_csv(path, parse_dates=["Date"])
    return to_wide(df) if wide else df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    prices = batch_download(["AAPL", "MSFT", "NOVO-B.CO", "^GSPC"], period="1mo")
    print("Opening prices:\n", get_opening_prices(prices).tail())
    print("\nClosing prices:\n", get_closing_prices(prices).tail())
