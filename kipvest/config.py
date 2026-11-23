"""Central configuration for Kipvest.

Default parameters taken from DOCS/SPEC.md. Modules use these as defaults so
strategies can be tuned in one place.
"""

# --- Data ingestion (SPEC §2) ---------------------------------------------
TRACKED_TICKERS: list[str] = [
    # US Tech & Semis
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "AVGO", "QCOM",
    # US Financials & Payments
    "JPM", "BAC", "GS", "MS", "V", "MA",
    # US Energy & Industrials
    "XOM", "CVX", "COP", "CAT", "DE", "UPS", "FDX",
    # US Healthcare & Staples
    "JNJ", "PFE", "MRK", "ABBV", "KO", "PEP", "WMT", "COST", "HD", "LOW",
    # US Telecom & Autos
    "VZ", "T", "F", "GM",
    # Copenhagen (.CO)
    "NOVO-B.CO", "GMAB.CO", "COLO-B.CO", "DEMANT.CO",
    "MAERSK-B.CO", "DSV.CO", "ORSTED.CO", "VWS.CO",
    "DANSKE.CO", "TRYG.CO", "CARL-B.CO", "RBREW.CO", "PNDORA.CO",
    # ETFs
    "SPY", "QQQ",
]
BENCHMARKS = {
    "sp500": "^GSPC",
    "omxc25": "^OMXC25",
}
DEFAULT_BENCHMARK = BENCHMARKS["sp500"]
HISTORY_PERIOD = "2y"  # enough warm-up for 50-day EMA and cointegration tests

# --- Trend / Momentum (SPEC §3.1) -----------------------------------------
EMA_FAST = 20
EMA_SLOW = 50
RSI_WINDOW = 14
ROC_WINDOW = 10

# --- Pairs / Mean Reversion (SPEC §3.2) -----------------------------------
COINTEGRATION_PVALUE = 0.05
ZSCORE_WINDOW = 20
ZSCORE_ENTRY = 2.0

# --- Volatility & Regime (SPEC §3.3) --------------------------------------
VOLATILITY_WINDOW = 20
ATR_WINDOW = 14
TRADING_DAYS_PER_YEAR = 252

# --- Monte Carlo (SPEC §3.4) ----------------------------------------------
MC_PATHS = 1_000
MC_HORIZON_DAYS = 5  # or 20
VAR_CONFIDENCE = 0.95

# --- Decision pipeline (SPEC §4) ------------------------------------------
DEAD_ZONE = 0.4

# --- Trade simulation (SPEC §5) -------------------------------------------
STARTING_CAPITAL = 100_000.0
