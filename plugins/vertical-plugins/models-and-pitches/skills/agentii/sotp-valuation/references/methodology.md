# sotp-valuation — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured segment financials via `search_xbrl_facts` + `get_statement_structure` .
- Branch (c) for MD&A segment narrative via `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_companies`.

## Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` .
2. **Segment discovery**: call `get_statement_structure(accession_number)` to identify segment-level concepts. Navigate from `Revenues` → segment children (ProductOrServiceAxis members).
3. **Segment financials**: query `search_xbrl_facts` for each segment's revenue, operating income, EBITDA, assets.
4. **Segment narrative**: `search_documents` + `read_source_pages` for MD&A segment discussion — business description, competitive position, growth outlook.
5. **Segment valuation**: assign appropriate multiple per segment based on industry comparables from `_cross/` outputs or sector norms:
 - High-growth segments → EV/Revenue
 - Mature/profitable segments → EV/EBITDA
 - Financial segments → P/B
 - Asset-heavy segments → EV/EBITDA
6. **Corporate adjustments**: subtract unallocated corporate overhead (capitalized at segment multiple), net debt, minority interest, add excess cash.
7. **SOTP bridge**: Segment A value + Segment B value + ... - Corporate Overhead - Net Debt + Cash = Total Equity Value ÷ Shares Outstanding = Per-Share Value.
8. **Output**: per with YAML frontmatter .
