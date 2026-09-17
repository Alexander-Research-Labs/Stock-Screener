# Value Investing Stock Screen

A quantitative value-investing screener built from a written thesis (see `Thesis.pdf`) by me and leveraging Ai to assist with code.

Informational & educational purposes only. Nothing here is a recommendation, offer, or solicitation to buy, sell, or hold any security.

# Functionality

Each day during the week it scans the watchlist. Any stocks that fits the requirements are send to Discord through webhook. Reach thesis to learn more.

# Set Up

pip install -r requirements.txt

cp .env.example .env

Fill in `.env`

python run_screen.py

# Data

SEC EDGAR - financial statements

Wikipedia - S&P 500 constituent list

Alpaca - daily price bars for SMA/EMA/MACD/Stochastic RSI, market cap, EV, and the 26-week pullback filter | Broker

Google News - recent headlines per stock

Claude - rates the headlines 1–9 for the News Sentiment score

Financial Modeling Prep - consensus EPS estimates, snapshotted over time to compute the Earnings Revision Score.

# Known Flaws

No backtest (No point for a bot that shows contenders that day; Also introduced survivorship bias from peer universe.

SEC SIC codes instead of GICS sub-industry so it's less organized. 

Earnings Revision Score needs a Financial Modeling Prep ~90 days of accumulated runs before it produces a real value once key gets added.

# Output

Every run posts one message to Discord (and saves the same result to `state/latest_run.json`):

**Contenders** - tickers that cleared both the F-Score gate and the V-Score discount bar, ranked by composite score.

**No contenders** - if nothing cleared the bar, the top contenders and their scores aren't posted; "runner ups" are posted instead.

**Strongest businesses** - the top 5 by F-Score alone, regardless of valuation.

**Excluded** - every watchlist ticker that didn't make it through, with a one line reason (stale filing, failed solvency check, not an operating company, etc.).



# Layout

Disclaimer Ai wrote this portion of the codebase.

run_screen.py - entry point, runs the full screen for every symbol in watchlist.json

config.py - every threshold from the thesis in one place

screen/fundamentals.py - pulls financials from SEC EDGAR

screen/classification.py - sector/industry from SIC codes, S&P 500 peer list, operating-company check

screen/market_data.py - prices and technicals from Alpaca

screen/news.py - headlines + Claude sentiment

screen/estimates.py - consensus EPS snapshots for the Earnings Revision Score

screen/scores.py - F-Score and V-Score

screen/peer_ranking.py - percentile ranking against S&P 500 peers

screen/composite.py - the weighted 10-point score

screen/financials_screen.py - separate scoring path for the Financials sector

screen/gate.py - qualify / contenders / strongest businesses logic

screen/report.py - formats and saves the daily output

state/ — daily run history, committed back by the GitHub Action

### Informational & educational purposes only. Nothing here is a recommendation, offer, or solicitation to buy, sell, or hold any security.
