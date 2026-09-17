import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests

import config

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en"


def recent_headlines(symbol, limit=10):
    try:
        resp = requests.get(
            GOOGLE_NEWS_RSS.format(query=quote(symbol)),
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        return [item.findtext("title", "") for item in root.iter("item")][:limit]
    except Exception:
        return []


def sentiment_score(symbol):
    headlines = recent_headlines(symbol)
    if not headlines:
        return None

    tool = {
        "name": "record_sentiment",
        "description": "Rate the overall sentiment of these headlines for this stock",
        "input_schema": {
            "type": "object",
            "properties": {
                "score": {"type": "integer", "minimum": 1, "maximum": 9},
                "reason": {"type": "string"},
            },
            "required": ["score", "reason"],
        },
    }
    prompt = (
        f"Rate the overall sentiment of recent news for {symbol} on a 1-9 scale, "
        "where 1 is very negative (fraud, bankruptcy risk, major scandal), 5 is neutral "
        "or mixed, and 9 is very positive (strong results, positive analyst coverage, "
        "good news flow). Base this only on the headlines below, not general knowledge "
        "of the company.\n\nHeadlines:\n" + "\n".join(f"- {h}" for h in headlines)
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": config.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": config.ANTHROPIC_MODEL,
                "max_tokens": 300,
                "tools": [tool],
                "tool_choice": {"type": "tool", "name": "record_sentiment"},
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        body = resp.json()
        for block in body.get("content", []):
            if block.get("type") == "tool_use":
                return int(block["input"]["score"])
    except Exception:
        return None
    return None
