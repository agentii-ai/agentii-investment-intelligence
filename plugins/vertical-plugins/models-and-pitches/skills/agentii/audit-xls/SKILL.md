---
name: audit-xls
multi_ticker_semantics: single_target
description: Audit spreadsheet, formula error detection, hardcoded cell finder, cross-sheet reference audit, workbook auditor, Excel model audit, financial model QA, spreadsheet review, cell dependency trace, formula integrity check
temporal_scope:
 default_quarters: 1
 max_quarters: 1
 description: "Typical lookback: 1 quarters, max: 1"
allowed_tools:
 - search_companies
 - get_company_financials
 - get_calculation_tree
 - validate_calculation
 - list_sources
retrieval_scope: simple_lookup
min_tool_diversity: 3
---

# audit-xls


## Triggers

- Audit spreadsheet
- formula error detection
- hardcoded cell finder
- cross-sheet reference audit
- workbook auditor
- Excel model audit
- financial model QA
- spreadsheet review
- cell dependency trace
- formula integrity check

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 1 | Standard lookback for this skill type |

## Methodology

### 1. Retrieval Scope

This skill operates with `retrieval_scope: simple_lookup`. It uses only profile/entity metadata tools — no document or XBRL retrieval at scale.

### 2. Retrieval Strategy

Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **(d) Simple Lookup**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

### 3. Temporal Scope

Default lookback: 1 fiscal quarter(s); maximum: 1. The default balances recency against the trend window this analysis requires.

### 4. Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_companies` — ticker resolution + company context (entity-alias fuzzy match)
- `get_company_financials` — consolidated IS/BS/CF highlights
- `get_calculation_tree` — XBRL calculation linkbase (weights)
- `validate_calculation` — XBRL calc-consistency validation
- `list_sources` — used by this skill per the retrieval strategy

### 5. Protocol

1. **Pre-flight**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`.
2. **Lookup**: `get_company_profile/{ticker}` / `get_entity_knowledge` for the requested metadata field(s).
3. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`.

## Deliverable Chain

**Inputs** → **Build** → **Validate** → **Output** → **Next**

1. **Inputs**: resolved ticker + structured facts (`search_xbrl_facts`, `get_company_financials`) and any filing pages from the three-layer protocol.
2. **Build**: assemble the workbook/deck spec and call `xlsx.build` / `pptx.build` (office plane).
3. **Validate**: run `xlsx.audit` (or recalc) and the `## Validation Gates` below.
4. **Output**: write the artifact path per `## Output File`.
5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.

## Validation Gates

1. **calculation arc cross-validation **: workbook computed totals verified against `gold.xbrl_calculations` weights. Compare `get_calculation_tree/{ticker}` expected values against workbook formulas. Flag discrepancies ≥1% of parent concept value. *If failed*: If material discrepancy (≥5%): refuse delivery. If minor (1-5%): flag in audit findings with `severity: warning`.
2. **hardcoded cell detection**: zero hardcoded values in cells tagged as formulas. Use `xlsx_audit` hardcoded-count output. *If failed*: If hardcoded_count > 0: refuse delivery with audit report listing each hardcoded cell location.
3. **cross-sheet reference integrity**: all cross-sheet references resolve to valid cell ranges. *If failed*: If broken references found: refuse delivery with broken reference map.
4. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (3). *If failed*: flag as depth-insufficient in Coverage Gaps.

## Output File

Write the final deliverable to `{ticker}/{{YYYY-MM-DD_HHMM}}_audit-xls_{{affix}}.md` .

## Output Structure

Write to `{ticker}/{YYYY-MM-DD_HHMM}_audit-xls_{affix}.md` (see `## Output File`).

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
