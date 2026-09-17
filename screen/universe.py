import json
from pathlib import Path

import config

WATCHLIST_FILE = Path(config.WATCHLIST_PATH)
PRIOR_RUN_FILE = Path(config.PRIOR_RUN_PATH)


def load_watchlist():
    if not WATCHLIST_FILE.exists():
        return []
    return json.loads(WATCHLIST_FILE.read_text())


def load_prior_eligible():
    if not PRIOR_RUN_FILE.exists():
        return set()
    data = json.loads(PRIOR_RUN_FILE.read_text())
    return set(data.get("eligible_symbols", []))


def save_prior_eligible(eligible_symbols):
    PRIOR_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRIOR_RUN_FILE.write_text(json.dumps({"eligible_symbols": sorted(eligible_symbols)}, indent=1))


def passes_pullback_filter(price, week26_high, was_eligible_prior_run):
    if price is None or week26_high is None or week26_high == 0:
        return False, "missing price/26w-high data"
    distance = (week26_high - price) / week26_high
    if was_eligible_prior_run:
        if distance >= config.PULLBACK_EXIT_PCT:
            return True, None
        return False, f"within {config.PULLBACK_EXIT_PCT:.1%} of 26w high (prior-run hysteresis)"
    if distance >= config.PULLBACK_ENTRY_PCT:
        return True, None
    return False, f"within {config.PULLBACK_ENTRY_PCT:.1%} of 26w high"


def passes_micro_cap_filter(market_cap):
    if market_cap is None:
        return False, "market cap unavailable"
    if market_cap < config.MICRO_CAP_FLOOR:
        return False, f"market cap ${market_cap:,.0f} below ${config.MICRO_CAP_FLOOR:,.0f} floor"
    return True, None
