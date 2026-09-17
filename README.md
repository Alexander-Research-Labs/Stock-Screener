# Value Investing Stock Screen

A quantitative value-investing screener built from a written thesis (see `Thesis.pdf`). AI-leveraged code, hand-written strategy.

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
