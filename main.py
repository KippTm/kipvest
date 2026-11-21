"""Kipvest daily entry point.

Fetches prices, runs the decision pipeline, and updates the simulated
portfolio.
"""

from kipvest import fetcher, pipeline, simulator  # noqa: F401  (used once implemented)


def run_daily() -> None:
    """Fetch today's data, generate decisions, and execute simulated trades."""
    raise NotImplementedError


def main() -> None:
    run_daily()


if __name__ == "__main__":
    main()
