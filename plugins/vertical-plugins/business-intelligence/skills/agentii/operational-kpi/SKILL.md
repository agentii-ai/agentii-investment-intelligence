---
name: operational-kpi
multi_ticker_semantics: single_target
description: Operational KPI tracking, headcount trends, utilization rates, backlog analysis, book-to-bill ratio, operational efficiency metrics, capacity utilization, productivity metrics, operational leverage, same-store sales
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - get_company_financials
 - get_company_profile
 - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 7
---

# operational-kpi


## Triggers

- Operational KPI tracking
- headcount trends
- utilization rates
- backlog analysis
- book-to-bill ratio
- operational efficiency metrics
- capacity utilization
- productivity metrics
- operational leverage
- same-store sales

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

### 1. Retrieval Scope

This skill operates with `retrieval_scope: structured_only`. It performs structured data retrieval only (XBRL facts, financials, earnings calendar) — no unstructured document search. Document-retrieval tools are excluded from `allowed_tools`.

### 2. Retrieval Strategy

Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

### 3. Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 8. The default balances recency against the trend window this analysis requires.

### 4. Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_companies` — ticker resolution + company context (entity-alias fuzzy match)
- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `get_company_financials` — consolidated IS/BS/CF highlights
- `get_company_profile` — sector/industry classification + metadata
- `list_xbrl_concepts` — US-GAAP concept discovery for non-standard line items

### 5. Protocol

1. **Pre-flight (mandatory)**: call `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`; route on coverage.
2. **Concept discovery** (non-standard concepts only): `list_xbrl_concepts(query=<term>, ticker=<T>)`.
3. **Structured retrieval**: `search_xbrl_facts(ticker, concept=[...], fiscal_year=[...])` (is_primary default) and/or `get_company_financials/{ticker}`.
4. **Batch rule**: 3+ same-tool queries → consolidate via `batch_search` (≤8 sub-queries).
5. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`.

## Output File

Write the final deliverable to `{ticker}/{{YYYY-MM-DD_HHMM}}_operational-kpi_{{affix}}.md` .

## Output Structure

Write to `{ticker}/{YYYY-MM-DD_HHMM}_operational-kpi_{affix}.md` (see `## Output File`).

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
