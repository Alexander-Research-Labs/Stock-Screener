import json
from datetime import date, timedelta
from pathlib import Path

import requests

import config

SNAPSHOT_FILE = Path(config.EPS_SNAPSHOT_PATH)
REVISION_LOOKBACK_DAYS = 90


def _load_snapshots():
    if not SNAPSHOT_FILE.exists():
        return {}
    return json.loads(SNAPSHOT_FILE.read_text())


def _save_snapshots(snapshots):
    SNAPSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(snapshots, indent=1))


def fetch_consensus_eps(symbol):
    if not config.FMP_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://financialmodelingprep.com/stable/analyst-estimates",
            params={"symbol": symbol, "period": "quarter", "limit": 1, "apikey": config.FMP_API_KEY},
            timeout=20,
        )
        resp.raise_for_status()
        rows = resp.json()
    except Exception:
        return None
    return rows[0].get("epsAvg") if rows else None


def earnings_revision_pct(symbol):
    current = fetch_consensus_eps(symbol)
    if current is None:
        return None

    snapshots = _load_snapshots()
    history = snapshots.get(symbol, [])
    today = date.today()
    cutoff = today - timedelta(days=REVISION_LOOKBACK_DAYS)

    baseline = None
    for entry in history:
        if date.fromisoformat(entry["date"]) <= cutoff:
            baseline = entry

    history.append({"date": today.isoformat(), "eps_avg": current})
    snapshots[symbol] = history[-400:]
    _save_snapshots(snapshots)

    if not baseline or not baseline["eps_avg"]:
        return None
    return (current - baseline["eps_avg"]) / abs(baseline["eps_avg"])
