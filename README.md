# Value Investing Stock Screen

A quantitative value-investing screener built from a written thesis (see `Thesis.pdf`). AI-assisted build, hand-written strategy.

Informational & educational purposes only. Nothing here is a recommendation, offer, or solicitation to buy, sell, or hold any security.

## What it does

Each weekday morning, the screen runs against your watchlist (`watchlist.json`) and:

1. Filters out micro-caps, stocks too close to their 26-week high, and anything with unreadable or stale SEC financial data
2. Routes financial-sector stocks (banks, insurers) to a separate scoring path, since their fundamentals don't compare to industrial companies
3. Scores every remaining stock on two independent 9-point scales:
   - **F-Score** — business quality (profitability, leverage, efficiency trends)
   - **V-Score** — how much of a discount it's trading at (valuation, momentum, sentiment)
4. A stock needs F-Score ≥ 5 to qualify and V-Score ≥ 6.5 to be recommended
5. Posts the day's recommendations, the top 5 businesses by quality alone, and anything excluded (with why) to Discord

## Data sources

- **Fundamentals** — SEC EDGAR XBRL filings, directly, no vendor
- **Sector/industry classification** — SEC SIC codes, same approach Alexander Research Labs uses
- **Price history & technicals** — Alpaca Market Data
- **News sentiment** — Google News headlines, rated by Claude
- **Peer universe** — current S&P 500 constituents (Wikipedia) for cross-sectional percentile ranking

## Setup

```
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
- `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` — a free Alpaca paper account works
- `ANTHROPIC_API_KEY` — for news sentiment scoring
- `DISCORD_WEBHOOK_URL` — optional, where the daily report posts

```
python run_screen.py
```

## Layout

```
config.py              every threshold from the thesis, in one place
run_screen.py           orchestrates the full daily run
screen/
  fundamentals.py       SEC EDGAR XBRL fetch + annual history extraction
  classification.py     SIC-based sector classification, S&P 500 peer universe
  market_data.py         Alpaca price history + technical indicators
  news.py                headline fetch + Claude sentiment scoring
  peer_ranking.py        cross-sectional percentile ranking against the S&P 500
  scores.py              F-Score and V-Score computation
  financials_screen.py   separate scoring path for the Financials sector
  composite.py            weighted composite score
  gate.py                 quality gate, discount bar, ranking, strongest businesses
  universe.py             watchlist loading, entry filters
  report.py               Discord formatting, state persistence
watchlist.json          the tracked universe
state/                  daily run output, carried forward for the pullback hysteresis
```

## Known gaps

- **Earnings Revision Score** — the thesis calls for 3-month consensus EPS revision, which needs an analyst-estimates data source not yet wired up. Currently scores as unavailable (0 on that V-Score check) rather than guessed.
- **Sub-industry peer matching** — true GICS Sub-Industry isn't available from free data. Peer grouping uses SEC's own industry description as a best-effort match, falling back to GICS Sector when that group is too small — same fallback the thesis specifies.
- **Security-type filtering** — ETFs, funds, and other non-equity instruments are currently identified only by "no matching SEC filer," not a true type classifier.
