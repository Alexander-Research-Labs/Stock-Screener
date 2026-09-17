import config


def weighted_composite(fundamentals_pct, relative_peer_valuation_pct, risk_pct, price_momentum_pct):
    parts = {
        "fundamentals": (fundamentals_pct, config.COMPOSITE_WEIGHTS["fundamentals"]),
        "relative_peer_valuation": (relative_peer_valuation_pct, config.COMPOSITE_WEIGHTS["relative_peer_valuation"]),
        "risk": (risk_pct, config.COMPOSITE_WEIGHTS["risk"]),
        "price_momentum": (price_momentum_pct, config.COMPOSITE_WEIGHTS["price_momentum"]),
    }
    total = 0.0
    weight_used = 0.0
    breakdown = {}
    for name, (pct, weight) in parts.items():
        if pct is None:
            breakdown[name] = None
            continue
        contribution = (pct / 100.0) * weight
        total += contribution
        weight_used += weight
        breakdown[name] = contribution
    score = (total / weight_used * sum(w for _, w in parts.values())) if weight_used else None
    return score, breakdown
