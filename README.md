# Value Investing Stock Screen

A quantitative value-investing screener built from a written thesis (see `Thesis.pdf`). AI-leveraged code, hand-written strategy.

Informational & educational purposes only. Nothing here is a recommendation, offer, or solicitation to buy, sell, or hold any security.

## What it does

Runs against your watchlist (`watchlist.json`) each weekday morning. Filters out micro-caps, stocks too close to their 26-week high, and anything with unreadable or stale SEC data. Scores what's left on two 9-point scales — F-Score for business quality, V-Score for how much of a discount it's trading at — and routes financial-sector stocks (banks, insurers) to their own scoring path, since their fundamentals don't compare to industrial companies. A stock needs F-Score ≥ 5 to qualify and V-Score ≥ 6.5 to be recommended. Posts the day's recommendations, the top 5 businesses by quality alone, and anything excluded (with why) to Discord.

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

## Not finished yet

- **Earnings Revision Score** has no free data source wired up — it's skipped, not guessed.
- **Interest coverage on a company that stops reporting it** (found via Apple's own filings — real debt, just no tagged interest expense in recent years) currently excludes the stock outright. Possibly too strict.
- **Sub-industry peer matching** uses SEC's industry description, not true GICS Sub-Industry — falls back to sector-level when that's too imprecise.
- **Non-equity filtering** (ETFs, funds, etc.) only checks for "no matching SEC filer" — not a real type check.
