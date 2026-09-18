# Quantitative Strategy

*Informational & educational purposes only. Nothing provided here is a recommendation, offer, or solicitation to buy, sell, or hold any security.*

**Strategy Title:** Value Investing Stock Screen
**Target Universe:** watchlist.json
**Target Capacity:** N/A / watchlist.js
**Rebalance Frequency:** Daily at 7:AM EST

## 1. Universe Definition & Entry Filter

- **Initial Universe:** My Current Watchlist
- **Cap Focus:** Iterate through my watchlist
- **Security Type:** Screen ordinary equities only.
- **Micro-cap Exclusion:** Drop any stock with a market cap below $300M
- **Pullback Filter:** Remove any stock coming off their 26-week high or within 2%. A name on the prior run's list stays eligible until it comes back within 0.5% of that high, so a stock drifting either side of the line does not enter and exit on price noise.
- **Unscoreable Filters:** Filter tickers that cannot be read from SEC us-gaap XBRL. Covers IFRS-only filers and non-USD reporters.
- **Stale Data:** Any metric whose newest annual filing is more than 800 days old is ineligible to get picked.

## 2. Sector Routing

Financial Sector are routed to a separate screen due to different business structure. See Section 9.

## 3. Value & Quality Factor Ranking (Cross-Sectional)

Percentile ranks (0 to 100) against S&P 500 constituents, using the finest peer group large enough to be meaningful: GICS Sub-Industry first, then GICS Sector, then the full universe.

- **EV / EBIT VS 3-Year Median:** Historical years priced using the current share count against split-adjusted prices, so splits do not corrupt the comparison.
- **Free Cash Flow Yield:** Free cash flow divided by market cap.
- **Profitability:** Gross Profit divided by Total Assets. Where a filer publishes no gross profit line, use EBIT divided by Total Assets. The two bases are ranked in separate cohorts, never against each other.
- **Industry/Company News:** Rated 1 to 9 from company headlines
- **Earnings Revision Score:** Percentage change in consensus EPS estimates over the last 3 months.
- **Revenue Growth Stability:** Standard deviation of year-over-year revenue growth.

## 4. Hard Exclusion Safety Screens

- **Solvency Check:** Interest Coverage Ratio above 2.0.
- **Liquidity Check:** Modified Quick Ratio above 1.0, defined as (Cash + Equivalents + Short-term Investments + Receivables) / (Current Liabilities minus Deferred Revenue).
- **Data Cleaning:** Drop a ticker only if a core ranking metric is missing (Eg. Enterprise Value, EBIT, Free Cash Flow, or the Profitability ratio). Secondary metrics get the sector median or a neutral 50th-percentile rank.

## 5. Technical & Momentum Indicators

- 50-day and 200-day Simple Moving Averages
- 14-day Stochastic RSI
- MACD line and Signal line
- 9-period and 21-period Exponential Moving Average

## 6. Weighted Composite 10 Point Scoring Model

- **Fundamentals:** 4.0
- **Relative Peer Valuation:** 3.5
- **Risk:** 2.0
- **Price Momentum:** 0.5

## 7. The 9-Point F-Score (Quality Rating)

**Profitability (4):** ROA > 0 · Operating Cash Flow > 0 · ROA improving · Operating CF > Net Income

**Leverage, Liquidity & Funds (3):** leverage falling or zero both periods · current ratio improving · no dilution

**Operating Efficiency (2):** gross margin improving · asset turnover improving

## 8. The 9-Point V-Score (Discount Rating)

Absolute conditions, so all nine can fail at once. Each scores 1.0 (Pass), 0.5 (near miss), 0 otherwise.

| # | Check | Full point | Half point |
|---|-------|-----------|-----------|
| 1 | Historical Value | EV/EBIT < 1.00x its 3-year median | < 1.15x |
| 2 | Absolute Valuation | EV/EBIT < 15 OR < 0.85x own median | < 22 OR < 0.95x |
| 3 | Free Cash Flow Return | FCF yield > 5% OR above own median | > 3% OR > 0.90x |
| 4 | Profitability | > 30% | > 20% |
| 5 | Steady revenue | growth standard deviation < 0.10 | < 0.15 |
| 6 | Upward Earnings Revisions | revisions > 0 | > −3% |
| 7 | Pullback | > 20% below 26-week high | > 12% |
| 8 | Short-Term Oversold | Stochastic RSI < 0.30 | < 0.45 |
| 9 | News Sentiment | sentiment ≥ 6 | ≥ 5 |

Checks 2 and 3 score on a self referential basis.

**Backstop:** EV/EBIT above 60 caps the total to 5.0 points. (Avoids buying stocks in a bubble)

## 9. Financials Screen

Scored on their own metrics, ranked only against each other.

- **Valuation (3.5):** Price-to-Book, Price-to-Earnings. P/E only counts when earnings are positive.
- **Fundamentals (4.0):** Return on Equity, Return on Assets, Revenue Growth Stability
- **Risk (2.0):** News sentiment, 90-day volatility, 1-year max drawdown
- **Momentum (0.5):** Same technical indicators
- **Capitalisation Floor:** Equity divided by Assets above 3%
- **6-Point F-Score, gated at 4:** Omits Leverage Trend, Liquidity Trend and Gross Margin Trend, none of which transfer to a balance-sheet business

## 10. Gate

- **Quality Gate:** F-Score must reach 5 of 9 to qualify.
- **Discount Bar:** V-Score must reach 6.5 of 9 to be recommended.
- **Ranking:** Among names clearing both, rank on the Weighted Composite.
- **Strongest Businesses:** top 5 by F-Score alone

## 11. Output

- **Recommendations:** tickers that clear the discount bar get put in a new list and "Strongest businesses" (Section 10) gets reported everyday at 7:AM EST
- **No Contenders:** If nothing clears the bar that week, outputs top contenders and their rating.

---

**Disclaimer:** Informational & educational purposes only. Nothing provided here is a recommendation, offer, or solicitation to buy, sell, or hold any security. All data and analytics are provided "AS IS" and "AS AVAILABLE," without warranty of any kind, and users are solely responsible for their own decisions and use of this data. Past performance is not indicative of future results.
