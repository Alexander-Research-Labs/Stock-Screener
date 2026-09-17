import config


def _at(values, idx):
    if values is None or idx is None or idx < 0 or idx >= len(values):
        return None
    return values[idx]


def gross_profit_of(revenue, gross_profit, cost_of_revenue):
    if gross_profit is not None:
        return gross_profit
    if revenue is not None and cost_of_revenue is not None:
        return revenue - cost_of_revenue
    return None


def compute_derived_metrics(hist):
    v = hist["values"]
    n = len(hist["periods"])
    out = []
    for i in range(n):
        revenue = _at(v["revenue"], i)
        ebit = _at(v["ebit"], i)
        net_income = _at(v["netIncome"], i)
        total_assets = _at(v["totalAssets"], i)
        equity = _at(v["stockholdersEquity"], i)
        lt_debt = _at(v["longTermDebt"], i) or 0
        st_debt = _at(v["shortTermDebt"], i) or 0
        ocf = _at(v["operatingCashFlow"], i)
        capex = _at(v["capex"], i)
        current_assets = _at(v["currentAssets"], i)
        current_liabilities = _at(v["currentLiabilities"], i)
        cash = _at(v["cashAndEquivalents"], i) or 0
        sti = _at(v["shortTermInvestments"], i) or 0
        receivables = _at(v["receivables"], i) or 0
        deferred_revenue = _at(v["deferredRevenue"], i) or 0
        interest_expense = _at(v["interestExpense"], i)
        diluted_shares = _at(v["dilutedShares"], i)
        gross_profit = gross_profit_of(revenue, _at(v["grossProfit"], i), _at(v["costOfRevenue"], i))

        fcf = (ocf - capex) if (ocf is not None and capex is not None) else None
        total_debt = lt_debt + st_debt
        leverage = (total_debt / total_assets) if total_assets else None
        roa = (net_income / total_assets) if (net_income is not None and total_assets) else None
        current_ratio = (current_assets / current_liabilities) if (current_assets is not None and current_liabilities) else None
        quick_ratio = (
            (cash + sti + receivables) / (current_liabilities - deferred_revenue)
            if (current_liabilities is not None and (current_liabilities - deferred_revenue) > 0)
            else None
        )
        if ebit is not None and interest_expense:
            interest_coverage = ebit / interest_expense
        elif total_debt == 0:
            interest_coverage = float("inf")
        else:
            interest_coverage = None
        gross_margin = (gross_profit / revenue) if (gross_profit is not None and revenue) else None
        profitability_gp = (gross_profit / total_assets) if (gross_profit is not None and total_assets) else None
        profitability_ebit = (ebit / total_assets) if (ebit is not None and total_assets) else None
        asset_turnover = (revenue / total_assets) if (revenue is not None and total_assets) else None
        revenue_growth = None

        out.append({
            "revenue": revenue, "ebit": ebit, "net_income": net_income, "total_assets": total_assets,
            "equity": equity, "total_debt": total_debt, "leverage": leverage, "ocf": ocf, "fcf": fcf,
            "roa": roa, "current_ratio": current_ratio, "quick_ratio": quick_ratio,
            "interest_coverage": interest_coverage, "gross_margin": gross_margin,
            "profitability_gp": profitability_gp, "profitability_ebit": profitability_ebit,
            "asset_turnover": asset_turnover, "diluted_shares": diluted_shares,
            "revenue_growth": revenue_growth,
        })

    for i in range(1, n):
        if out[i]["revenue"] and out[i - 1]["revenue"]:
            out[i]["revenue_growth"] = (out[i]["revenue"] - out[i - 1]["revenue"]) / abs(out[i - 1]["revenue"])

    return out


def f_score(metrics):
    if len(metrics) < 2:
        return None, {}
    curr, prior = metrics[-1], metrics[-2]
    checks = {}

    checks["roa_positive"] = curr["roa"] is not None and curr["roa"] > 0
    checks["ocf_positive"] = curr["ocf"] is not None and curr["ocf"] > 0
    checks["roa_improving"] = (
        curr["roa"] is not None and prior["roa"] is not None and curr["roa"] > prior["roa"]
    )
    checks["ocf_over_net_income"] = (
        curr["ocf"] is not None and curr["net_income"] is not None and curr["ocf"] > curr["net_income"]
    )

    checks["leverage_falling"] = (
        curr["leverage"] is not None and prior["leverage"] is not None and (
            curr["leverage"] < prior["leverage"] or (curr["leverage"] == 0 and prior["leverage"] == 0)
        )
    )
    checks["current_ratio_improving"] = (
        curr["current_ratio"] is not None and prior["current_ratio"] is not None
        and curr["current_ratio"] > prior["current_ratio"]
    )
    checks["no_dilution"] = (
        curr["diluted_shares"] is not None and prior["diluted_shares"] is not None
        and curr["diluted_shares"] <= prior["diluted_shares"]
    )

    checks["gross_margin_improving"] = (
        curr["gross_margin"] is not None and prior["gross_margin"] is not None
        and curr["gross_margin"] > prior["gross_margin"]
    )
    checks["asset_turnover_improving"] = (
        curr["asset_turnover"] is not None and prior["asset_turnover"] is not None
        and curr["asset_turnover"] > prior["asset_turnover"]
    )

    score = sum(1 for v in checks.values() if v)
    return score, checks


def financials_f_score(metrics):
    if len(metrics) < 2:
        return None, {}
    curr, prior = metrics[-1], metrics[-2]
    checks = {
        "roa_positive": curr["roa"] is not None and curr["roa"] > 0,
        "ocf_positive": curr["ocf"] is not None and curr["ocf"] > 0,
        "roa_improving": curr["roa"] is not None and prior["roa"] is not None and curr["roa"] > prior["roa"],
        "ocf_over_net_income": curr["ocf"] is not None and curr["net_income"] is not None and curr["ocf"] > curr["net_income"],
    }
    score = sum(1 for v in checks.values() if v)
    return score, checks


def _score_check(value, thresholds, higher_is_better=True):
    if value is None:
        return 0.0
    full, half = thresholds["full"], thresholds["half"]
    if higher_is_better:
        if value > full:
            return 1.0
        if value > half:
            return 0.5
        return 0.0
    if value < full:
        return 1.0
    if value < half:
        return 0.5
    return 0.0


def v_score(ev_ebit_now, ev_ebit_3yr_median, fcf_yield, fcf_yield_own_median,
            profitability, revenue_growth_stdev, earnings_revision_pct,
            pullback_pct, stochastic_rsi, news_sentiment):
    checks = {}

    hist_value_ratio = (ev_ebit_now / ev_ebit_3yr_median) if (ev_ebit_now is not None and ev_ebit_3yr_median) else None
    checks["historical_value"] = _score_check(hist_value_ratio, config.V_SCORE_CHECKS["historical_value"], higher_is_better=False)

    abs_val_multiple = _score_check(ev_ebit_now, config.V_SCORE_CHECKS["absolute_valuation_multiple"], higher_is_better=False)
    abs_val_own_median = 0.0
    if ev_ebit_now is not None and ev_ebit_3yr_median:
        ratio = ev_ebit_now / ev_ebit_3yr_median
        abs_val_own_median = _score_check(ratio, config.V_SCORE_CHECKS["absolute_valuation_own_median"], higher_is_better=False)
    checks["absolute_valuation"] = max(abs_val_multiple, abs_val_own_median)

    fcf_multiple = _score_check(fcf_yield, config.V_SCORE_CHECKS["fcf_yield"], higher_is_better=True)
    fcf_own_median = 0.0
    if fcf_yield is not None and fcf_yield_own_median:
        ratio = fcf_yield / fcf_yield_own_median
        fcf_own_median = _score_check(ratio, config.V_SCORE_CHECKS["fcf_own_median"], higher_is_better=True)
    checks["fcf_return"] = max(fcf_multiple, fcf_own_median)

    checks["profitability"] = _score_check(profitability, config.V_SCORE_CHECKS["profitability"], higher_is_better=True)
    checks["steady_revenue_growth"] = _score_check(revenue_growth_stdev, config.V_SCORE_CHECKS["revenue_stability_stdev"], higher_is_better=False)
    checks["upward_earnings_revisions"] = _score_check(earnings_revision_pct, config.V_SCORE_CHECKS["earnings_revisions"], higher_is_better=True)
    checks["pullback"] = _score_check(pullback_pct, config.V_SCORE_CHECKS["pullback"], higher_is_better=True)
    checks["short_term_oversold"] = _score_check(stochastic_rsi, config.V_SCORE_CHECKS["stochastic_rsi"], higher_is_better=False)
    checks["news_sentiment"] = _score_check(news_sentiment, config.V_SCORE_CHECKS["news_sentiment"], higher_is_better=True)

    total = sum(checks.values())
    if ev_ebit_now is not None and ev_ebit_now > config.EV_EBIT_BUBBLE_BACKSTOP:
        total = min(total, config.EV_EBIT_BACKSTOP_CAP)

    return total, checks
