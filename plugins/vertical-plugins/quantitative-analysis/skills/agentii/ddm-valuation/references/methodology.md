# ddm-valuation — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

## Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Applicability check**: `search_xbrl_facts(ticker, concept=["Dividends", "CommonStockDividendsPerShareDeclared"], fiscal_year=[latest, latest-1, latest-2, latest-3, latest-4])` and `get_realtime_quote(ticker)` for dividend_yield. If no dividend history: flag "DDM not applicable — company does not pay dividends. Use DCF or Residual Income instead."
3. **Dividend profile**: compute historical DPS growth rate (3yr/5yr CAGR), payout ratio (DPS / EPS), dividend coverage (EPS / DPS >1.5 = comfortable).
4. **Cost of equity**: CAPM — risk-free rate (10Y UST), equity risk premium (~5%), beta from `get_realtime_quote`. Ke = Rf + β × ERP.
5. **Multi-stage model**:
 - **Stage 1 (Explicit)**: forecast DPS for next 5 years using consensus EPS × payout ratio (from `search_earnings_calendar`).
 - **Stage 2 (Transition)**: DPS growth linearly declines from Stage 1 rate to terminal growth rate over 5 years.
 - **Stage 3 (Maturity)**: perpetual DPS growing at terminal rate (Gordon Growth: TV = DPS_terminal × (1+g) / (Ke - g).
6. **Fair value**: PV of Stage 1 dividends + PV of Stage 2 dividends + PV of terminal value = per-share fair value.
7. **Output**: per with YAML frontmatter .
