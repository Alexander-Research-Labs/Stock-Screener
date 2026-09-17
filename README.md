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

SEC EDGAR, Wikipedia, Alpaca, Google News, Claude, Financial Modeling Prep.
