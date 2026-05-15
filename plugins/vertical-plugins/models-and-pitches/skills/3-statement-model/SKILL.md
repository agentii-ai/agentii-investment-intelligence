---
name: 3-statement-model
description: '3-statement integrated financial model: IS/BS/CFS triangulation, 5 historical
  + 5 forecast years, driver-based projection.'
multi_ticker_semantics: single_target
parameter_free: false
temporal_scope:
  default_quarters: 12
  max_quarters: 20
  description: 'Financial modeling: trailing 12 quarters (3 fiscal years) for long-range
    projection inputs'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
- xlsx.build
- xlsx.recalc
- xlsx.evaluate
- xlsx.audit
---

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze 3 statement model
- run 3 statement model analysis
- produce 3 statement model report
- 3 statement model breakdown
- 3 statement model deep dive
- build a 3 statement model
- assess 3 statement model
- quantify 3 statement model
- compare 3 statement model across peers
- review 3 statement model for
- generate 3 statement model on
- 3 statement model for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |





## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale across SEC filings (10-K, 10-Q, 8-K). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies per spec 023 FR-056.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries via `search_cross_period`.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

### Temporal Scope

Default: 12 fiscal quarters (max 20). Financial modeling: trailing 12 quarters (3 fiscal years) for long-range projection inputs.

### Tool Allowlist

See frontmatter `allowed_tools` — 12 tools declared for this vertical.

### Protocol

1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.
2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.
3. Retrieval: follow the three-layer protocol —
   - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.
   - Layer 2: `read_source_outline` to scan page-level metadata.
   - Layer 2.5 (optional): `search_keyword_in_source` to filter large documents.
   - Layer 3: `read_source_pages` to deep-read only selected pages.
4. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per FR-046b.

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include per FR-020a: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
