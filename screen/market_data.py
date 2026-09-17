import os
from datetime import date, timedelta

import numpy as np
import pandas as pd
import requests

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_DATA_URL = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets/v2")

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
}


def _to_alpaca(symbol):
    return symbol.replace("-", ".")


def daily_bars(symbol, lookback_days=380):
    end = date.today()
    start = end - timedelta(days=lookback_days)
    resp = requests.get(
        f"{ALPACA_DATA_URL}/stocks/{_to_alpaca(symbol)}/bars",
        headers=HEADERS,
        params={
            "timeframe": "1Day",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "feed": "iex",
            "limit": 10000,
        },
        timeout=30,
    )
    resp.raise_for_status()
    bars = resp.json().get("bars", [])
    if not bars:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    df = pd.DataFrame(bars)
    df = df.rename(columns={"t": "date", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["date", "open", "high", "low", "close", "volume"]]


def latest_trade_price(symbol):
    resp = requests.get(
        f"{ALPACA_DATA_URL}/stocks/{_to_alpaca(symbol)}/trades/latest",
        headers=HEADERS,
        params={"feed": "iex"},
        timeout=15,
    )
    resp.raise_for_status()
    trade = resp.json().get("trade") or {}
    price = trade.get("p")
    return float(price) if price else None


def sma(closes, window):
    if len(closes) < window:
        return None
    return float(np.mean(closes[-window:]))


def ema_series(closes, span):
    return pd.Series(closes).ewm(span=span, adjust=False).mean()


def ema(closes, span):
    if len(closes) < span:
        return None
    return float(ema_series(closes, span).iloc[-1])


def macd(closes):
    if len(closes) < 26:
        return None, None
    macd_line = ema_series(closes, 12) - ema_series(closes, 26)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return float(macd_line.iloc[-1]), float(signal_line.iloc[-1])


def stochastic_rsi(closes, rsi_period=14, stoch_period=14):
    series = pd.Series(closes)
    if len(series) < rsi_period + stoch_period:
        return None
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / rsi_period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / rsi_period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(100)
    recent = rsi.iloc[-stoch_period:]
    lo, hi = recent.min(), recent.max()
    if hi == lo:
        return 0.5
    return float((rsi.iloc[-1] - lo) / (hi - lo))


def week26_high(df):
    if df.empty:
        return None
    cutoff = date.today() - timedelta(weeks=26)
    window = df[df["date"] >= cutoff]
    if window.empty:
        return None
    return float(window["high"].max())


def volatility_90d(df):
    closes = df["close"].tail(91)
    if len(closes) < 2:
        return None
    returns = closes.pct_change().dropna()
    return float(returns.std() * np.sqrt(252))


def max_drawdown_1y(df):
    closes = df["close"].tail(253)
    if closes.empty:
        return None
    running_max = closes.cummax()
    drawdown = (closes - running_max) / running_max
    return float(drawdown.min())


def momentum_score_pct(sma_50, sma_200, ema_9, ema_21, macd_line, macd_signal, stoch_rsi):
    parts = []
    if sma_50 is not None and sma_200 is not None:
        parts.append(100.0 if sma_50 > sma_200 else 0.0)
    if ema_9 is not None and ema_21 is not None:
        parts.append(100.0 if ema_9 > ema_21 else 0.0)
    if macd_line is not None and macd_signal is not None:
        parts.append(100.0 if macd_line > macd_signal else 0.0)
    if stoch_rsi is not None:
        parts.append(stoch_rsi * 100.0)
    if not parts:
        return None
    return sum(parts) / len(parts)


def technical_snapshot(symbol):
    df = daily_bars(symbol)
    if df.empty or len(df) < 30:
        return None
    closes = df["close"].tolist()
    latest_close = closes[-1]
    return {
        "price": latest_close,
        "sma_50": sma(closes, 50),
        "sma_200": sma(closes, 200),
        "ema_9": ema(closes, 9),
        "ema_21": ema(closes, 21),
        "macd_line": macd(closes)[0],
        "macd_signal": macd(closes)[1],
        "stochastic_rsi": stochastic_rsi(closes),
        "week26_high": week26_high(df),
        "volatility_90d": volatility_90d(df),
        "max_drawdown_1y": max_drawdown_1y(df),
        "bars": df,
    }
