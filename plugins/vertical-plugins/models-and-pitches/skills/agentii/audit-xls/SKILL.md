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
 - xlsx-read
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

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(d) Simple Lookup**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

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
2. **Build**: perform the formula / hardcoded-cell / cross-sheet-reference audit on the input workbook and write the `.md` audit report per `## Output Structure`.
3. **Validate**: run the `## Validation Gates` below.
4. **Output**: write the artifact path per `## Output File`.
5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.

## Validation Gates

1. **calculation arc cross-validation **: workbook computed totals verified against `gold.xbrl_calculations` weights. Compare `get_calculation_tree/{ticker}` expected values against workbook formulas. Flag discrepancies ≥1% of parent concept value. *If failed*: If material discrepancy (≥5%): refuse delivery. If minor (1-5%): flag in audit findings with `severity: warning`.
2. **hardcoded cell detection**: zero hardcoded values in cells tagged as formulas. Use `xlsx_audit` hardcoded-count output. *If failed*: If hardcoded_count > 0: refuse delivery with audit report listing each hardcoded cell location.
3. **cross-sheet reference integrity**: all cross-sheet references resolve to valid cell ranges. *If failed*: If broken references found: refuse delivery with broken reference map.
4. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (3). *If failed*: flag as depth-insufficient in Coverage Gaps.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_audit-xls_{affix}.md` .

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
