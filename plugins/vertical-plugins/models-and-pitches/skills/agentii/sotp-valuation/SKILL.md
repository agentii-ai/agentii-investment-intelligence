---
name: sotp-valuation
description: Sum of the Parts valuation, segment-based valuation, conglomerate valuation, business segment analysis, breakup value, segment sum valuation, parts worth more than whole, hidden asset value
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Latest segment data with up to 12 quarters for segment trend"
allowed_tools:
  - search_xbrl_facts
  - search_companies
  - get_realtime_quote
  - search_documents
  - read_source_outline
  - read_source_pages
  - get_statement_structure
retrieval_scope: unstructured_document_search
min_tool_diversity: 7
---

# Sum of the Parts (SOTP) Valuation

Values each business segment independently and sums for total enterprise value. Essential for conglomerates (GE, MMM, HON), multi-segment tech (AMZN: AWS + Retail + Ads, GOOG: Search + Cloud + YouTube), and holding companies. SOTP often reveals "hidden value" when the market undervalues individual segments.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution (FR-082)** and **Workspace style.md override check (FR-094)** apply. **`get_realtime_quote` availability (FR-105)**: If not deployed, sector multiples from `_cross/` comps outputs (FR-093) can substitute for current market data. Segment valuation is relative, not price-dependent.

## Triggers

- sum of the parts valuation {ticker}
- SOTP analysis {ticker}
- segment-based valuation {ticker}
- breakup value {ticker}
- conglomerate valuation {ticker}
- parts worth more than whole {ticker}
- segment sum of parts {ticker}
- business segment valuation {ticker}
- hidden asset value {ticker}
- SOTP {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| segment_discovery | statement_tree | Use get_statement_structure for segment identification |
| peer_multiples | sector | Apply sector-appropriate multiples per segment |
| include_corporate | true | Subtract corporate overhead, net debt |

## Methodology

### Retrieval Scope

`unstructured_document_search` — SOTP requires segment financials from XBRL (structured) AND segment narrative/business description from MD&A (unstructured) for appropriate multiple selection.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured segment financials via `search_xbrl_facts` + `get_statement_structure` (FR-085).
- Branch (c) for MD&A segment narrative via `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_companies`.

### Protocol

1. **Pre-retrieval**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}` (FR-075).
2. **Segment discovery**: call `get_statement_structure/{ticker}?statement_type=income_statement&fiscal_year=<latest>` to identify segment-level concepts. Navigate from `Revenues` → segment children (ProductOrServiceAxis members).
3. **Segment financials**: query `search_xbrl_facts` for each segment's revenue, operating income, EBITDA, assets.
4. **Segment narrative**: `search_documents` + `read_source_pages` for MD&A segment discussion — business description, competitive position, growth outlook.
5. **Segment valuation**: assign appropriate multiple per segment based on industry comparables from `_cross/` outputs (FR-093) or sector norms:
   - High-growth segments → EV/Revenue
   - Mature/profitable segments → EV/EBITDA
   - Financial segments → P/B
   - Asset-heavy segments → EV/EBITDA
6. **Corporate adjustments**: subtract unallocated corporate overhead (capitalized at segment multiple), net debt, minority interest, add excess cash.
7. **SOTP bridge**: Segment A value + Segment B value + ... - Corporate Overhead - Net Debt + Cash = Total Equity Value ÷ Shares Outstanding = Per-Share Value.
8. **Output**: per FR-079 with YAML frontmatter (FR-090).

## Output File

Write to `{ticker}/{YYYY-MM-DD_HHMM}_sotp-valuation_segment-sum.md` per FR-079.

## Output Structure

1. **Executive Summary** — SOTP per-share value, premium/discount to current price, key value driver segment
2. **Segment Identification** — segments discovered via statement tree, business description per segment
3. **Segment Financials** — revenue, EBITDA, operating income, assets per segment with growth rates
4. **Segment Valuation** — multiple selection rationale, comparable companies, per-segment enterprise value
5. **SOTP Bridge** — segment-by-segment value → corporate overhead → net debt → cash → equity value → per-share
6. **Sensitivity** — per-share value at ±1x multiple for key segments
7. **Coverage Gaps & Citations**

**Citation density**: ≥1 citation per 200 words. **Citation link format (FR-081)**: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. **agentii.md append (FR-087)** applies.

## Validation Gates

1. **Segment coverage**: segment revenues must sum to ≥80% of total reported revenue. *If failed*: flag segments representing <80% of revenue; note "significant unallocated revenue."
2. **Valuation consistency**: segment multiples justified by at least one comparable company or sector norm per segment. *If failed*: flag segments with unsubstantiated multiples.
3. **SOTP bridge integrity**: Segment Sum - Corporate + Adjustments = Total Equity within 1%. *If failed*: refuse delivery; check bridge arithmetic.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_statement_structure` | Tree unavailable | Use `search_documents` for "segment" keyword in 10-K MD&A |
| `read_source_pages` | SQL error | Use `search_documents` for segment narrative; flag as partial |

## Error Handling

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| No segment data | Company reports as single segment | "{ticker} reports as a single operating segment — SOTP not applicable. Use DCF or comps." |
| Missing segment financials | Proceed with available data; flag gaps | "Segment financials incomplete for {segment_names}; SOTP based on partial data." |
