"""Kipvest daily entry point.

Fetches prices, runs the decision pipeline, and updates the simulated
portfolio.
"""
import pandas as pd
from kipvest import fetcher, pipeline, simulator, config  # noqa: F401  (used once implemented)


def run_daily() -> None:
    """Fetch today's data, generate decisions, and execute simulated trades."""
    raise NotImplementedError


def main() -> None:
    run_daily()


if __name__ == "__main__":
    tickers = [*config.TRACKED_TICKERS,
    config.DEFAULT_BENCHMARK]
    prices = fetcher.batch_download(tickers,
    period=config.HISTORY_PERIOD)
    prices.to_pickle("data/prices.pkl")
    prices.to_csv("data/prices.csv")

    opens = fetcher.get_opening_prices(prices)
    closes = fetcher.get_closing_prices(prices)
    print(closes.tail())
    #main()
