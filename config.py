import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "Alexander Research Labs contact@alexanderresearchlabs.com")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

MICRO_CAP_FLOOR = 300_000_000
PULLBACK_ENTRY_PCT = 0.02
PULLBACK_EXIT_PCT = 0.005
STALE_DATA_DAYS = 800
MIN_PEER_GROUP_SIZE = 5

INTEREST_COVERAGE_MIN = 2.0
QUICK_RATIO_MIN = 1.0

COMPOSITE_WEIGHTS = {
    "fundamentals": 4.0,
    "relative_peer_valuation": 3.5,
    "risk": 2.0,
    "price_momentum": 0.5,
}

F_SCORE_QUALIFY_MIN = 5
V_SCORE_RECOMMEND_MIN = 6.5
STRONGEST_BUSINESSES_COUNT = 5

EV_EBIT_BUBBLE_BACKSTOP = 60
EV_EBIT_BACKSTOP_CAP = 5.0

FINANCIALS_CAP_FLOOR_EQUITY_TO_ASSETS = 0.03
FINANCIALS_F_SCORE_GATE_MIN = 4

V_SCORE_CHECKS = {
    "historical_value": {"full": 1.00, "half": 1.15},
    "absolute_valuation_multiple": {"full": 15, "half": 22},
    "absolute_valuation_own_median": {"full": 0.85, "half": 0.95},
    "fcf_yield": {"full": 0.05, "half": 0.03},
    "fcf_own_median": {"full": 1.00, "half": 0.90},
    "profitability": {"full": 0.30, "half": 0.20},
    "revenue_stability_stdev": {"full": 0.10, "half": 0.15},
    "earnings_revisions": {"full": 0.0, "half": -0.03},
    "pullback": {"full": 0.20, "half": 0.12},
    "stochastic_rsi": {"full": 0.30, "half": 0.45},
    "news_sentiment": {"full": 6, "half": 5},
}

WATCHLIST_PATH = "watchlist.json"
PRIOR_RUN_PATH = "state/prior_run.json"
OUTPUT_PATH = "state/latest_run.json"
EPS_SNAPSHOT_PATH = "state/eps_estimates.json"
