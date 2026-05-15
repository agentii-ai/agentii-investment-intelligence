---
name: competitive-positioning
description: 'Competitive positioning: Porter''s Five Forces, moat assessment, strategic-group
  analysis, and positioning map.'
multi_ticker_semantics: target_with_optional_peers
parameter_free: false
temporal_scope:
  default_quarters: 8
  max_quarters: 12
  description: 'Industry analysis: trailing 8 quarters for peer trajectory and competitive
    dynamics'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
- get_entity_knowledge
- search_companies
- search_sec_filings
---

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze competitive positioning
- run competitive positioning analysis
- produce competitive positioning report
- competitive positioning breakdown
- competitive positioning deep dive
- build a competitive positioning
- assess competitive positioning
- quantify competitive positioning
- compare competitive positioning across peers
- review competitive positioning for
- generate competitive positioning on
- competitive positioning for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |





## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale across SEC filings (10-K, 10-Q, 8-K). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries via `search_cross_period`.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

### Temporal Scope

Default: 8 fiscal quarters (max 12). Industry analysis: trailing 8 quarters for peer trajectory and competitive dynamics.

### Tool Allowlist

See frontmatter `allowed_tools` — 11 tools declared for this vertical.

### Protocol

1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.
2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.
3. Retrieval: follow the three-layer protocol —
   - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.
   - Layer 2: `read_source_outline` to scan page-level metadata.
   - Layer 2.5 (optional): `search_keyword_in_source` to filter large documents.
   - Layer 3: `read_source_pages` to deep-read only selected pages.
4. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per the evidence-pack output contract.

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
| Knowledge Store unavailable | `get_entity_knowledge` returns HTTP 503 `DATA_NOT_AVAILABLE` | Fall back to `get_company_profile` + `search_companies` + `search_documents` for competitive context; flag output with `knowledge_store_degraded: true` | "Knowledge Store not yet available; analysis based on filing-derived competitive context." |
