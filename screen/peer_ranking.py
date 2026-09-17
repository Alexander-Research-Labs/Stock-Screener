import numpy as np
import pandas as pd

import config


def percentile_rank(value, peer_values):
    clean = [v for v in peer_values if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if value is None or len(clean) < config.MIN_PEER_GROUP_SIZE:
        return None
    arr = np.array(clean, dtype=float)
    return float((arr < value).sum() / len(arr) * 100)


def peer_group_for(symbol, sic_industry_desc, gics_sector, sp500_metrics_df):
    if sic_industry_desc:
        sub = sp500_metrics_df[
            (sp500_metrics_df["symbol"] != symbol)
            & (sp500_metrics_df["gics_sub_industry"] == sic_industry_desc)
        ]
        if len(sub) >= config.MIN_PEER_GROUP_SIZE:
            return sub, "sub_industry"

    if gics_sector:
        sector = sp500_metrics_df[
            (sp500_metrics_df["symbol"] != symbol)
            & (sp500_metrics_df["gics_sector"] == gics_sector)
        ]
        if len(sector) >= config.MIN_PEER_GROUP_SIZE:
            return sector, "sector"

    return sp500_metrics_df[sp500_metrics_df["symbol"] != symbol], "full_universe"


def rank_against_peers(symbol, metric_name, value, sic_industry_desc, gics_sector, sp500_metrics_df):
    peers, level = peer_group_for(symbol, sic_industry_desc, gics_sector, sp500_metrics_df)
    peer_values = peers[metric_name].tolist() if metric_name in peers.columns else []
    return percentile_rank(value, peer_values), level


def median_of(values):
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return float(np.median(clean))


def stdev_of(values):
    clean = [v for v in values if v is not None]
    if len(clean) < 2:
        return None
    return float(np.std(clean, ddof=1))
