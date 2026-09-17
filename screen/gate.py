import config


def apply_gates(scored_candidates):
    qualified = [
        c for c in scored_candidates
        if c.get("f_score") is not None and c["f_score"] >= config.F_SCORE_QUALIFY_MIN
    ]
    recommended = [
        c for c in qualified
        if c.get("v_score") is not None and c["v_score"] >= config.V_SCORE_RECOMMEND_MIN
    ]
    recommended.sort(key=lambda c: (c.get("composite_score") or 0), reverse=True)

    strongest = sorted(
        [c for c in scored_candidates if c.get("f_score") is not None],
        key=lambda c: c["f_score"],
        reverse=True,
    )[:config.STRONGEST_BUSINESSES_COUNT]

    if not recommended:
        top_contenders = sorted(
            [c for c in qualified if c.get("v_score") is not None],
            key=lambda c: c["v_score"],
            reverse=True,
        )[:config.STRONGEST_BUSINESSES_COUNT]
        return {
            "recommendations": [],
            "no_contenders": True,
            "top_contenders": top_contenders,
            "strongest_businesses": strongest,
        }

    return {
        "recommendations": recommended,
        "no_contenders": False,
        "top_contenders": [],
        "strongest_businesses": strongest,
    }
