import io

import pandas as pd
import requests

import config

SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SP500_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ARL-research/1.0; contact@alexanderresearchlabs.com)"}

SIC_SECTOR_RANGES = [
    (100, 999, "Consumer Staples"),
    (1000, 1099, "Materials"),
    (1200, 1299, "Energy"),
    (1300, 1399, "Energy"),
    (1400, 1499, "Materials"),
    (1500, 1799, "Industrials"),
    (2000, 2199, "Consumer Staples"),
    (2200, 2299, "Consumer Discretionary"),
    (2300, 2399, "Consumer Discretionary"),
    (2400, 2499, "Materials"),
    (2500, 2599, "Consumer Discretionary"),
    (2600, 2699, "Materials"),
    (2700, 2799, "Communication Services"),
    (2800, 2829, "Materials"),
    (2830, 2836, "Health Care"),
    (2837, 2844, "Consumer Staples"),
    (2845, 2899, "Materials"),
    (2900, 2999, "Energy"),
    (3000, 3099, "Materials"),
    (3100, 3199, "Consumer Discretionary"),
    (3200, 3299, "Materials"),
    (3300, 3399, "Materials"),
    (3400, 3499, "Industrials"),
    (3500, 3569, "Industrials"),
    (3570, 3579, "Information Technology"),
    (3580, 3599, "Industrials"),
    (3600, 3699, "Information Technology"),
    (3700, 3711, "Consumer Discretionary"),
    (3712, 3799, "Industrials"),
    (3800, 3840, "Industrials"),
    (3841, 3845, "Health Care"),
    (3846, 3899, "Industrials"),
    (3900, 3999, "Consumer Discretionary"),
    (4000, 4599, "Industrials"),
    (4600, 4699, "Energy"),
    (4700, 4799, "Industrials"),
    (4800, 4899, "Communication Services"),
    (4900, 4999, "Utilities"),
    (5000, 5199, "Industrials"),
    (5300, 5399, "Consumer Discretionary"),
    (5400, 5499, "Consumer Staples"),
    (5500, 5599, "Consumer Discretionary"),
    (5900, 5912, "Consumer Staples"),
    (5200, 5999, "Consumer Discretionary"),
    (6000, 6299, "Financials"),
    (6300, 6499, "Financials"),
    (6500, 6599, "Real Estate"),
    (6798, 6798, "Real Estate"),
    (6700, 6799, "Financials"),
    (7000, 7099, "Consumer Discretionary"),
    (7200, 7299, "Consumer Discretionary"),
    (7370, 7379, "Information Technology"),
    (7300, 7399, "Industrials"),
    (7500, 7599, "Consumer Discretionary"),
    (7600, 7699, "Industrials"),
    (7800, 7899, "Communication Services"),
    (7900, 7999, "Consumer Discretionary"),
    (8000, 8099, "Health Care"),
    (8200, 8299, "Consumer Discretionary"),
    (8100, 8999, "Industrials"),
]

FINANCIALS_GICS_SECTOR = "Financials"


def sic_to_sector(sic_code):
    try:
        n = int(sic_code)
    except (TypeError, ValueError):
        return None
    for lo, hi, sector in SIC_SECTOR_RANGES:
        if lo <= n <= hi:
            return sector
    return None


def clean_sic_description(desc):
    if not isinstance(desc, str) or not desc.strip():
        return None
    titled = " ".join(w.capitalize() for w in desc.strip().lower().split())
    return titled.replace("Nec", "NEC")


def classify_from_submissions(submissions_json):
    sector = sic_to_sector(submissions_json.get("sic"))
    sic_industry = clean_sic_description(submissions_json.get("sicDescription"))
    return sector, sic_industry


_sp500_cache = None


def sp500_constituents():
    global _sp500_cache
    if _sp500_cache is not None:
        return _sp500_cache
    resp = requests.get(SP500_URL, headers=SP500_HEADERS, timeout=20)
    resp.raise_for_status()
    table = pd.read_html(io.StringIO(resp.text), header=0)[0]
    table = table.rename(columns={
        "Symbol": "symbol",
        "GICS Sector": "gics_sector",
        "GICS Sub-Industry": "gics_sub_industry",
        "CIK": "cik",
    })
    table["symbol"] = table["symbol"].str.replace(".", "-", regex=False)
    _sp500_cache = table[["symbol", "gics_sector", "gics_sub_industry", "cik"]]
    return _sp500_cache
