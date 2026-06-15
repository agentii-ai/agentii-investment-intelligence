---
name: unit-economics
multi_ticker_semantics: single_target
description: Unit economics analysis, CAC LTV estimation, churn inference, gross margin per unit, customer economics, subscription economics, per-unit profitability, contribution margin, payback period, cohort economics
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

# unit-economics

## Triggers

- Unit economics analysis
- CAC LTV estimation
- churn inference
- gross margin per unit
- customer economics
- subscription economics
- per-unit profitability
- contribution margin
- payback period
- cohort economics

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | 4 | Standard lookback for this skill type |

## Methodology

### 1. Retrieval Scope

This skill operates with `retrieval_scope: structured_only`. It performs structured data retrieval only (XBRL facts, financials, earnings calendar) — no unstructured document search. Document-retrieval tools are excluded from `allowed_tools`.

### 2. Retrieval Strategy

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

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

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_unit-economics_{affix}.md` .

## Output Structure

1. **Executive Summary** (≤200 words) — headline conclusions for the analysis.
2. **Data Sources** — filings + structured endpoints used, with `{ticker} {citation_id} page<N>` citations.
3. **Analysis** — the core findings, tables, and commentary for this dimension.
4. **Key Metrics** — the quantitative results with QoQ/YoY context where relevant.
5. **Coverage Gaps & Citations** — data not retrievable + citation index.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.

## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

## Error Handling

| Error | Action |
|-------|--------|
| Ticker not found | Suggest checking spelling or trying list_coverage |
| No data available | Flag in Coverage Gaps, proceed with available data |
| API key invalid | Direct user to agentii.ai/api-keys |
| MCP server unreachable | Retry once; if persistent, halt with AGENTII_MCP_UNREACHABLE |
