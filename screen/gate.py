import config


def apply_gates(scored_candidates):
    qualified = [
        c for c in scored_candidates
        if c.get("f_score") is not None and c["f_score"] >= config.F_SCORE_QUALIFY_MIN
    ]
    contenders = [
        c for c in qualified
        if c.get("v_score") is not None and c["v_score"] >= config.V_SCORE_RECOMMEND_MIN
    ]
    contenders.sort(key=lambda c: (c.get("composite_score") or 0), reverse=True)

    strongest = sorted(
        [c for c in scored_candidates if c.get("f_score") is not None],
        key=lambda c: c["f_score"],
        reverse=True,
    )[:config.STRONGEST_BUSINESSES_COUNT]

    if not contenders:
        runners_up = sorted(
            [c for c in qualified if c.get("v_score") is not None],
            key=lambda c: c["v_score"],
            reverse=True,
        )[:config.STRONGEST_BUSINESSES_COUNT]
        return {
            "contenders": [],
            "no_contenders": True,
            "runners_up": runners_up,
            "strongest_businesses": strongest,
        }

    return {
        "contenders": contenders,
        "no_contenders": False,
        "runners_up": [],
        "strongest_businesses": strongest,
    }
