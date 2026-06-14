---
name: peer-bench
multi_ticker_semantics: target_with_required_peers
description: Peer benchmarking, multi-ticker financial comparison, growth value matrix, composite z-score ranking, industry peer comparison, competitive benchmarking, sector relative performance, peer group analysis, industry leader comparison, financial ratio benchmarking
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Typical lookback: 4 quarters, max: 12"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - search_sec_filings
 - get_company_financials
 - batch_search
 - list_coverage
 - read_source_outline
 - read_source_deep_outline
 - list_xbrl_concepts
 - read_source_pages
 - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 7
---

# peer-bench


## Triggers

- Peer benchmarking
- multi-ticker financial comparison
- growth value matrix
- composite z-score ranking
- industry peer comparison
- competitive benchmarking
- sector relative performance
- peer group analysis
- industry leader comparison
- financial ratio benchmarking

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

### 1. Retrieval Scope

This skill operates with `retrieval_scope: unstructured_document_search`. It performs unstructured document search at scale via the three-layer retrieval protocol (Layer 1→2→2.5→3), escalating to `read_source_deep_outline` only when lightweight labels cannot disambiguate pages, plus structured XBRL where needed.

### 2. Retrieval Strategy

Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **(b)/(c) Unstructured Query via the three-layer protocol**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

### 3. Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 12. The default balances recency against the trend window this analysis requires.

### 4. Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_companies` — ticker resolution + company context (entity-alias fuzzy match)
- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `search_documents` — Layer 1 document discovery (page-level silver records)
- `search_sec_filings` — Layer 1 SEC filing metadata index
- `get_company_financials` — consolidated IS/BS/CF highlights
- `batch_search` — consolidate 3+ same-tool queries into one metered call
- `list_coverage` — universe-level coverage discovery
- `read_source_outline` — Layer 2 lightweight page map (description + keywords)
- `read_source_deep_outline` — Layer 2.5a deep page map (table_titles/drivers/metrics)
- `list_xbrl_concepts` — US-GAAP concept discovery for non-standard line items
- `read_source_pages` — Layer 3 deep read of selected pages with table markers
- `search_keyword_in_source` — Layer 2.5b keyword page filter for large documents

### 5. Protocol

1. **Pre-flight (mandatory)**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`; route on coverage.
2. **Layer 1 — discovery**: `search_documents` / `search_sec_filings` to find candidate filings by ticker/form_type/date.
3. **Layer 2 — page map**: `read_source_outline/{ticker}/{citation_id}`; skip NULL-description pages; escalate to `read_source_deep_outline` only when labels can't disambiguate.
4. **Layer 2.5 (optional)**: `search_keyword_in_source` to narrow documents >50 pages.
5. **Layer 3 — deep read**: `read_source_pages/{ticker}/{citation_id}?row_numbers=page<N>,...` for the 3–5 selected pages only.
6. **Multi-period** (if applicable): `search_cross_period` after fiscal-calendar resolution.
7. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`.

## Output File

Write the final deliverable to `_cross/{descriptive-slug}_{{YYYY-MM-DD_HHMM}}_peer-bench_{{affix}}.md` or `_sector/{sector_name}/{{YYYY-MM-DD_HHMM}}_peer-bench_{{affix}}.md` .

## Output Structure

Write to `{ticker}/{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md` (see `## Output File`).

1. **Executive Summary** (≤200 words) — headline conclusions for the analysis.
2. **Data Sources** — filings + structured endpoints used, with `{ticker} {citation_id} page<N>` citations.
3. **Analysis** — the core findings, tables, and commentary for this dimension.
4. **Key Metrics** — the quantitative results with QoQ/YoY context where relevant.
5. **Coverage Gaps & Citations** — data not retrievable + citation index.

**Citation density**: ≥1 citation per 200 words; bare `page_no` integers are forbidden — always cite as `{ticker} {citation_id} page<N>`. After writing, append a YAML block to `agentii.md` per `contracts/agentii-md-schema.md`.

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.

## Error Handling

| Error | Action |
|-------|--------|
| Ticker not found | Suggest checking spelling or trying list_coverage |
| No data available | Flag in Coverage Gaps, proceed with available data |
| API key invalid | Direct user to agentii.ai/api-keys |
| MCP server unreachable | Retry once; if persistent, halt with AGENTII_MCP_UNREACHABLE |
