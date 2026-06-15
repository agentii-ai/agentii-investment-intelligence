# peg-valuation — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts`.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_earnings_calendar`.

## Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Price data**: `get_realtime_quote(ticker)` → current stock price, PE (TTM), market cap, EPS (TTM).
3. **Consensus estimates**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest+1])` → consensus EPS (current year, next year), long-term growth rate estimate.
4. **Historical EPS (fallback)**: if consensus growth unavailable, `search_xbrl_facts(ticker, concept=["EarningsPerShareDiluted"], fiscal_year=[latest, latest-1, latest-2, latest-3, latest-4])` → compute 3yr and 5yr EPS CAGR.
5. **Compute PEG**:
 - PEG (LTM) = PE_TTM ÷ Consensus LTG (%)
 - PEG (NTM) = PE_NTM ÷ Consensus LTG (%)
 - PEG (Historical) = PE_TTM ÷ EPS CAGR_3yr (%)
6. **Peer PEG comparison**: `search_companies` for sector peers → get PE + growth for each → compute peer PEGs → mean/median/high/low comparison.
7. **Output**: per with YAML frontmatter .
