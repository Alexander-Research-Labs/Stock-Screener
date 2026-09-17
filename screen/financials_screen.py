import config
from screen.scores import financials_f_score


def score_financial(symbol, metrics, price, book_value_per_share, technical, news_sentiment, peer_pb, peer_pe, peer_roe, peer_roa):
    if not metrics or len(metrics) < 1:
        return None
    curr = metrics[-1]

    equity_to_assets = (curr["equity"] / curr["total_assets"]) if (curr["equity"] is not None and curr["total_assets"]) else None
    if equity_to_assets is None or equity_to_assets <= config.FINANCIALS_CAP_FLOOR_EQUITY_TO_ASSETS:
        return {"symbol": symbol, "eligible": False, "reason": "equity/assets below capitalisation floor"}

    f_score, f_checks = financials_f_score(metrics)
    if f_score is None or f_score < config.FINANCIALS_F_SCORE_GATE_MIN:
        return {"symbol": symbol, "eligible": False, "reason": "financials F-score below gate", "f_score": f_score}

    pb = (price / book_value_per_share) if (price is not None and book_value_per_share) else None
    pe = (price / (curr["net_income"] / curr["diluted_shares"])) if (
        curr["net_income"] is not None and curr["net_income"] > 0
        and curr["diluted_shares"] and price is not None
    ) else None

    valuation_rank_pb = peer_pb
    valuation_rank_pe = peer_pe
    fundamentals_rank_roe = peer_roe
    fundamentals_rank_roa = peer_roa

    risk = {
        "news_sentiment": news_sentiment,
        "volatility_90d": technical.get("volatility_90d") if technical else None,
        "max_drawdown_1y": technical.get("max_drawdown_1y") if technical else None,
    }
    momentum = {
        "sma_50": technical.get("sma_50") if technical else None,
        "sma_200": technical.get("sma_200") if technical else None,
        "macd_line": technical.get("macd_line") if technical else None,
        "macd_signal": technical.get("macd_signal") if technical else None,
        "stochastic_rsi": technical.get("stochastic_rsi") if technical else None,
    }

    return {
        "symbol": symbol,
        "eligible": True,
        "f_score": f_score,
        "f_checks": f_checks,
        "pb": pb,
        "pe": pe,
        "valuation_rank_pb": valuation_rank_pb,
        "valuation_rank_pe": valuation_rank_pe,
        "fundamentals_rank_roe": fundamentals_rank_roe,
        "fundamentals_rank_roa": fundamentals_rank_roa,
        "risk": risk,
        "momentum": momentum,
    }
