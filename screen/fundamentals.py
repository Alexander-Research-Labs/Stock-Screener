from datetime import date, datetime

import requests

import config

SEC_HEADERS = {"User-Agent": config.SEC_USER_AGENT}

TAG_CANDIDATES = {
    "revenue": {"tags": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"], "instant": False},
    "ebit": {"tags": ["OperatingIncomeLoss"], "instant": False},
    "grossProfit": {"tags": ["GrossProfit"], "instant": False},
    "costOfRevenue": {"tags": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"], "instant": False},
    "operatingCashFlow": {"tags": ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"], "instant": False},
    "capex": {"tags": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsForCapitalImprovements", "PaymentsToAcquireMachineryAndEquipment"], "instant": False},
    "netIncome": {"tags": ["NetIncomeLoss"], "instant": False},
    "totalAssets": {"tags": ["Assets"], "instant": True},
    "stockholdersEquity": {"tags": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "instant": True},
    "longTermDebt": {"tags": ["LongTermDebtNoncurrent", "LongTermDebt"], "instant": True},
    "shortTermDebt": {"tags": ["DebtCurrent", "ShortTermBorrowings"], "instant": True},
    "dilutedShares": {"tags": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], "instant": False},
    "currentAssets": {"tags": ["AssetsCurrent"], "instant": True},
    "currentLiabilities": {"tags": ["LiabilitiesCurrent"], "instant": True},
    "cashAndEquivalents": {"tags": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"], "instant": True},
    "shortTermInvestments": {"tags": ["ShortTermInvestments"], "instant": True},
    "receivables": {"tags": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"], "instant": True},
    "deferredRevenue": {"tags": ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent"], "instant": True},
    "interestExpense": {"tags": ["InterestExpense", "InterestExpenseDebt"], "instant": False},
    "cashFromFinancing": {"tags": ["NetCashProvidedByUsedInFinancingActivities"], "instant": False},
    "proceedsFromStockIssuance": {"tags": ["ProceedsFromIssuanceOfCommonStock", "StockIssuedDuringPeriodValueNewIssues"], "instant": False},
    "sharesOutstanding": {"tags": ["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"], "instant": True},
}


def resolve_cik(symbol):
    resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS, timeout=20)
    resp.raise_for_status()
    for row in resp.json().values():
        if row.get("ticker") == symbol:
            return row.get("cik_str")
    return None


def fetch_submissions(cik):
    padded = str(cik).zfill(10)
    resp = requests.get(f"https://data.sec.gov/submissions/CIK{padded}.json", headers=SEC_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_company_facts(cik):
    padded = str(cik).zfill(10)
    resp = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded}.json", headers=SEC_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _period_days(start, end):
    s = datetime.fromisoformat(start)
    e = datetime.fromisoformat(end)
    return (e - s).days


def _is_valid_annual_period(entry, instant):
    if not entry.get("end") or not isinstance(entry.get("val"), (int, float)):
        return False
    if instant:
        return entry.get("form") == "10-K" and entry.get("fp") == "FY"
    if not entry.get("start"):
        return False
    days = _period_days(entry["start"], entry["end"])
    return entry.get("form") == "10-K" and entry.get("fp") == "FY" and 340 <= days <= 380


def _extract_annual_series(facts_for_tag, instant):
    units = (facts_for_tag or {}).get("units", {})
    entries = units.get("USD", []) + units.get("shares", []) + units.get("USD/shares", [])
    valid = [e for e in entries if _is_valid_annual_period(e, instant)]
    by_end = {}
    for e in valid:
        existing = by_end.get(e["end"])
        if not existing or (e.get("filed") or "") > (existing.get("filed") or ""):
            by_end[e["end"]] = e
    return sorted(by_end.values(), key=lambda r: r["end"])


def _best_series(gaap_facts, candidate):
    by_end = {}
    for tag in candidate["tags"]:
        series = _extract_annual_series(gaap_facts.get(tag), candidate["instant"])
        for r in series:
            existing = by_end.get(r["end"])
            if not existing or (r.get("filed") or "") > (existing.get("filed") or ""):
                by_end[r["end"]] = r
    return sorted(by_end.values(), key=lambda r: r["end"])


def annual_history(company_facts, years=4):
    gaap_facts = (company_facts.get("facts") or {}).get("us-gaap", {})
    series_by_concept = {
        concept: _best_series(gaap_facts, candidate)
        for concept, candidate in TAG_CANDIDATES.items()
    }
    all_ends = sorted({r["end"] for series in series_by_concept.values() for r in series})
    if not all_ends:
        return {"periods": [], "values": {}, "newest_filed": None}
    periods = all_ends[-years:]
    values = {}
    newest_filed = None
    for concept, series in series_by_concept.items():
        by_end = {r["end"]: r for r in series}
        values[concept] = [by_end[p]["val"] if p in by_end else None for p in periods]
        for r in series:
            if r["end"] in periods and (newest_filed is None or (r.get("filed") or "") > newest_filed):
                newest_filed = r.get("filed")
    return {"periods": periods, "values": values, "newest_filed": newest_filed}


def is_stale(newest_filed):
    if not newest_filed:
        return True
    filed_date = datetime.fromisoformat(newest_filed).date()
    return (date.today() - filed_date).days > config.STALE_DATA_DAYS
