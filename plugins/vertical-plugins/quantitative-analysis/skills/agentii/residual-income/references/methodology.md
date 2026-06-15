# residual-income — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

## Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Book value**: `search_xbrl_facts(ticker, concept=["Equity", "StockholdersEquity"], fiscal_year=[latest])` — latest book value of equity.
3. **Earnings**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest+1, latest+2])` for consensus EPS estimates.
4. **Cost of equity (Ke)**: CAPM — Rf (10Y UST) + β × ERP (5%). β from `get_realtime_quote`.
5. **Forecast residual income**:
 - For each forecast year: RI_t = Net Income_t - (Ke × Beginning Book Value_t-1)
 - Book Value_t = Book Value_t-1 + Net Income_t - Dividends_t
 - Dividends_t = Net Income_t × Payout Ratio (historical average or zero if no dividend)
6. **Terminal value**: TV = RI_terminal × (1+g) / (Ke - g), where g is perpetuity growth (typically 0% or GDP-like rate for RI).
7. **Fair value**: BV_0 + PV(RI_1) + PV(RI_2) + ... + PV(RI_terminal) + PV(TV) = per-share equity value.
8. **Output**: per with YAML frontmatter .
