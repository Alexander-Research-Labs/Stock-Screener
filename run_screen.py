import sys

import pandas as pd

import config
from screen import classification, composite, fundamentals, gate, market_data, news, peer_ranking, report, scores, universe


def build_sp500_metrics():
    sp500 = classification.sp500_constituents()
    rows = []
    for _, row in sp500.iterrows():
        try:
            submissions = fundamentals.fetch_submissions(row["cik"])
        except Exception:
            continue
        if not classification.is_operating_company(submissions):
            continue
        gics_sector, sic_industry = classification.classify_from_submissions(submissions)

        try:
            facts = fundamentals.fetch_company_facts(row["cik"])
        except Exception:
            continue
        hist = fundamentals.annual_history(facts)
        if len(hist["periods"]) < 1:
            continue
        derived = scores.compute_derived_metrics(hist)
        curr = derived[-1]

        price = None
        try:
            price = market_data.latest_trade_price(row["symbol"])
        except Exception:
            pass

        market_cap = price * curr["diluted_shares"] if (price and curr["diluted_shares"]) else None
        cash = (hist["values"]["cashAndEquivalents"][-1] or 0)
        ev = (market_cap + (curr["total_debt"] or 0) - cash) if market_cap is not None else None
        ev_ebit = (ev / curr["ebit"]) if (ev is not None and curr["ebit"]) else None
        fcf_yield = (curr["fcf"] / market_cap) if (curr["fcf"] is not None and market_cap) else None
        revenue_growth_stdev = peer_ranking.stdev_of([d["revenue_growth"] for d in derived if d["revenue_growth"] is not None])

        rows.append({
            "symbol": row["symbol"],
            "gics_sector": gics_sector,
            "sic_industry": sic_industry,
            "profitability_gp": curr["profitability_gp"],
            "profitability_ebit": curr["profitability_ebit"],
            "roa": curr["roa"],
            "roe": (curr["net_income"] / curr["equity"]) if (curr["net_income"] is not None and curr["equity"]) else None,
            "ev_ebit": ev_ebit,
            "fcf_yield": fcf_yield,
            "revenue_growth_stdev": revenue_growth_stdev,
            "pb": (price / (curr["equity"] / curr["diluted_shares"])) if (price and curr["equity"] is not None and curr["diluted_shares"]) else None,
            "pe": (price / (curr["net_income"] / curr["diluted_shares"])) if (
                price and curr["net_income"] is not None and curr["net_income"] > 0 and curr["diluted_shares"]
            ) else None,
        })
    return pd.DataFrame(rows)


def screen_one(symbol, prior_eligible, sp500_metrics_df):
    cik = fundamentals.resolve_cik(symbol)
    if not cik:
        return None, {"symbol": symbol, "type": "unknown", "reason": "no SEC CIK match — not an operating-company equity filer, or unlisted"}

    submissions = fundamentals.fetch_submissions(cik)
    if not classification.is_operating_company(submissions):
        return None, {"symbol": symbol, "type": "non_equity", "reason": "SEC entityType is not 'operating' — likely an ETF, trust, or fund rather than a common-stock operating company"}
    gics_sector, sic_industry = classification.classify_from_submissions(submissions)

    facts = fundamentals.fetch_company_facts(cik)
    hist = fundamentals.annual_history(facts)
    if not hist["periods"]:
        return None, {"symbol": symbol, "reason": "unscoreable — no readable us-gaap XBRL"}
    if fundamentals.is_stale(hist["newest_filed"]):
        return None, {"symbol": symbol, "reason": f"stale data — newest filing older than {config.STALE_DATA_DAYS} days"}

    technical = market_data.technical_snapshot(symbol)
    if not technical:
        return None, {"symbol": symbol, "reason": "no price/technical data available"}

    ok, why = universe.passes_micro_cap_filter(
        technical["price"] * scores.compute_derived_metrics(hist)[-1]["diluted_shares"]
        if technical.get("price") and scores.compute_derived_metrics(hist)[-1]["diluted_shares"] else None
    )
    if not ok:
        return None, {"symbol": symbol, "reason": why}

    ok, why = universe.passes_pullback_filter(technical["price"], technical["week26_high"], symbol in prior_eligible)
    if not ok:
        return None, {"symbol": symbol, "reason": why}

    derived = scores.compute_derived_metrics(hist)
    curr = derived[-1]
    market_cap = technical["price"] * curr["diluted_shares"] if curr["diluted_shares"] else None
    total_debt = curr["total_debt"] or 0
    cash = (hist["values"]["cashAndEquivalents"][-1] or 0)
    ev = (market_cap + total_debt - cash) if market_cap is not None else None
    ev_ebit_now = (ev / curr["ebit"]) if (ev is not None and curr["ebit"]) else None
    ev_ebit_history = []
    for d in derived:
        e = (market_cap + total_debt - cash) if market_cap is not None else None
        ev_ebit_history.append((e / d["ebit"]) if (e is not None and d["ebit"]) else None)
    ev_ebit_3yr_median = peer_ranking.median_of(ev_ebit_history[-3:])

    fcf_yield = (curr["fcf"] / market_cap) if (curr["fcf"] is not None and market_cap) else None
    fcf_yields_history = [(d["fcf"] / market_cap) if (d["fcf"] is not None and market_cap) else None for d in derived]
    fcf_yield_own_median = peer_ranking.median_of(fcf_yields_history)

    profitability = curr["profitability_gp"] if curr["profitability_gp"] is not None else curr["profitability_ebit"]
    revenue_growth_stdev = peer_ranking.stdev_of([d["revenue_growth"] for d in derived if d["revenue_growth"] is not None])

    pullback_pct = (
        (technical["week26_high"] - technical["price"]) / technical["week26_high"]
        if technical.get("week26_high") and technical.get("price") else None
    )

    sentiment = news.sentiment_score(symbol)

    if gics_sector == classification.FINANCIALS_GICS_SECTOR:
        from screen.financials_screen import score_financial
        book_value_per_share = (curr["equity"] / curr["diluted_shares"]) if (curr["equity"] is not None and curr["diluted_shares"]) else None
        pb_now = (technical["price"] / book_value_per_share) if (technical.get("price") and book_value_per_share) else None
        pe_now = (technical["price"] / (curr["net_income"] / curr["diluted_shares"])) if (
            technical.get("price") and curr["net_income"] is not None and curr["net_income"] > 0 and curr["diluted_shares"]
        ) else None
        roe_now = (curr["net_income"] / curr["equity"]) if (curr["net_income"] is not None and curr["equity"]) else None
        peer_pb, _ = peer_ranking.rank_against_peers(symbol, "pb", pb_now, sic_industry, gics_sector, sp500_metrics_df)
        peer_pe, _ = peer_ranking.rank_against_peers(symbol, "pe", pe_now, sic_industry, gics_sector, sp500_metrics_df)
        peer_roe, _ = peer_ranking.rank_against_peers(symbol, "roe", roe_now, sic_industry, gics_sector, sp500_metrics_df)
        peer_roa, _ = peer_ranking.rank_against_peers(symbol, "roa", curr["roa"], sic_industry, gics_sector, sp500_metrics_df)
        result = score_financial(symbol, derived, technical["price"], book_value_per_share, technical, sentiment, peer_pb, peer_pe, peer_roe, peer_roa)
        if result is None or not result.get("eligible"):
            return None, {"symbol": symbol, "reason": (result or {}).get("reason", "ineligible financial")}
        v, v_checks = scores.v_score(
            ev_ebit_now, ev_ebit_3yr_median, fcf_yield, fcf_yield_own_median,
            profitability, revenue_growth_stdev, None, pullback_pct,
            technical.get("stochastic_rsi"), sentiment,
        )

        pb_pct = (100 - peer_pb) if peer_pb is not None else None
        pe_pct = (100 - peer_pe) if peer_pe is not None else None
        fin_valuation_parts = [p for p in [pb_pct, pe_pct] if p is not None]
        fin_valuation_pct = sum(fin_valuation_parts) / len(fin_valuation_parts) if fin_valuation_parts else None
        fin_fundamentals_parts = [p for p in [peer_roe, peer_roa] if p is not None]
        fin_fundamentals_pct = sum(fin_fundamentals_parts) / len(fin_fundamentals_parts) if fin_fundamentals_parts else None
        fin_risk_pct = ((sentiment / 9) * 100) if sentiment is not None else None
        fin_momentum_pct = market_data.momentum_score_pct(
            technical.get("sma_50"), technical.get("sma_200"),
            technical.get("ema_9"), technical.get("ema_21"),
            technical.get("macd_line"), technical.get("macd_signal"),
            technical.get("stochastic_rsi"),
        )
        fin_composite, fin_breakdown = composite.weighted_composite(
            fin_fundamentals_pct, fin_valuation_pct, fin_risk_pct, fin_momentum_pct
        )

        result.update({
            "v_score": v, "v_checks": v_checks, "screen": "financials",
            "composite_score": fin_composite, "composite_breakdown": fin_breakdown,
            "news_sentiment": sentiment,
        })
        return result, None

    interest_ok = curr["interest_coverage"] is None or curr["interest_coverage"] > config.INTEREST_COVERAGE_MIN
    quick_ok = curr["quick_ratio"] is not None and curr["quick_ratio"] > config.QUICK_RATIO_MIN
    if not (interest_ok and quick_ok):
        return None, {"symbol": symbol, "reason": "failed solvency/liquidity safety screen"}

    f, f_checks = scores.f_score(derived)
    v, v_checks = scores.v_score(
        ev_ebit_now, ev_ebit_3yr_median, fcf_yield, fcf_yield_own_median,
        profitability, revenue_growth_stdev, None, pullback_pct,
        technical.get("stochastic_rsi"), sentiment,
    )

    profitability_pct, _ = peer_ranking.rank_against_peers(symbol, "profitability_gp", profitability, sic_industry, gics_sector, sp500_metrics_df)
    revenue_stability_pct, _ = peer_ranking.rank_against_peers(symbol, "revenue_growth_stdev", revenue_growth_stdev, sic_industry, gics_sector, sp500_metrics_df)
    revenue_stability_pct = (100 - revenue_stability_pct) if revenue_stability_pct is not None else None
    fundamentals_parts = [p for p in [profitability_pct, revenue_stability_pct] if p is not None]
    fundamentals_pct = sum(fundamentals_parts) / len(fundamentals_parts) if fundamentals_parts else None

    ev_ebit_pct, _ = peer_ranking.rank_against_peers(symbol, "ev_ebit", ev_ebit_now, sic_industry, gics_sector, sp500_metrics_df)
    ev_ebit_pct = (100 - ev_ebit_pct) if ev_ebit_pct is not None else None
    fcf_yield_pct, _ = peer_ranking.rank_against_peers(symbol, "fcf_yield", fcf_yield, sic_industry, gics_sector, sp500_metrics_df)
    valuation_parts = [p for p in [ev_ebit_pct, fcf_yield_pct] if p is not None]
    valuation_pct = sum(valuation_parts) / len(valuation_parts) if valuation_parts else None

    momentum_pct = market_data.momentum_score_pct(
        technical.get("sma_50"), technical.get("sma_200"),
        technical.get("ema_9"), technical.get("ema_21"),
        technical.get("macd_line"), technical.get("macd_signal"),
        technical.get("stochastic_rsi"),
    )
    risk_pct = ((sentiment / 9) * 100) if sentiment is not None else None

    composite_score, composite_breakdown = composite.weighted_composite(
        fundamentals_pct, valuation_pct, risk_pct, momentum_pct
    )

    return {
        "symbol": symbol,
        "eligible": True,
        "screen": "standard",
        "gics_sector": gics_sector,
        "sic_industry": sic_industry,
        "f_score": f,
        "f_checks": f_checks,
        "v_score": v,
        "v_checks": v_checks,
        "ev_ebit": ev_ebit_now,
        "fcf_yield": fcf_yield,
        "profitability": profitability,
        "profitability_percentile": profitability_pct,
        "composite_score": composite_score,
        "composite_breakdown": composite_breakdown,
        "news_sentiment": sentiment,
        "technical": {k: v for k, v in technical.items() if k != "bars"},
    }, None


def main():
    watchlist = universe.load_watchlist()
    prior_eligible = universe.load_prior_eligible()

    print("Fetching S&P 500 peer universe (this takes a while, 500 SEC lookups)...")
    sp500_metrics_df = build_sp500_metrics()
    print(f"Peer universe ready: {len(sp500_metrics_df)} constituents scored.")

    scored, excluded, eligible_symbols = [], [], []
    for symbol in watchlist:
        result, exclusion = screen_one(symbol, prior_eligible, sp500_metrics_df)
        if result:
            scored.append(result)
            eligible_symbols.append(symbol)
        else:
            excluded.append(exclusion)

    universe.save_prior_eligible(eligible_symbols)

    result = gate.apply_gates(scored)
    result["excluded"] = excluded
    report.save_result(result)
    print(report.format_discord(result))

    if config.DISCORD_WEBHOOK_URL:
        import requests
        requests.post(config.DISCORD_WEBHOOK_URL, json={"content": report.format_discord(result)[:2000]}, timeout=20)

    return 0


if __name__ == "__main__":
    sys.exit(main())
