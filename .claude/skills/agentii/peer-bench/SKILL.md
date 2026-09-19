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
 - search_knowledge_entries
 - get_knowledge_entry
 - search_by_analogue
retrieval_scope: unstructured_document_search
min_tool_diversity: 9
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

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(b)/(c) Unstructured Query via the three-layer protocol**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

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
- `list_xbrl_concepts` — XBRL concept discovery for non-standard line items (`namespace` param; default `us-gaap` — use `ifrs-full` for foreign filers)
- `read_source_pages` — Layer 3 deep read of selected pages with table markers
- `search_keyword_in_source` — Layer 2.5b keyword page filter for large documents

### 5. Protocol

1. **Pre-flight (mandatory)**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`; route on coverage.
2. **Layer 1 — discovery**: `search_documents` / `search_sec_filings` to find candidate filings by ticker/form_type/date.
3. **Layer 2 — page map**: `read_source_outline/{ticker}/{citation_id}`; skip NULL-description pages; escalate to `read_source_deep_outline` only when labels can't disambiguate.
4. **Layer 2.5 (optional)**: `search_keyword_in_source` to narrow documents >50 pages.
5. **Layer 3 — deep read**: `read_source_pages/{ticker}/{citation_id}?pages=page<N>,...` for the 3–5 selected pages only.
6. **Multi-period** (if applicable): `search_cross_period` after fiscal-calendar resolution.
7. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`.

## Output File

Write the final deliverable to `_cross/{descriptive-slug}_{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md` or `_sector/{sector_name}/{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md` .

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

## References

- **Methodology**: [`references/methodology.md`](references/methodology.md) — tool fallbacks, retrieval strategy, analysis framework
- **Output Structure**: [`references/output-structure.md`](references/output-structure.md) — detailed deliverable sections and ordering

**Ownership & insider signals**: `search_institutional_holdings` (top-10 holders + whale portfolios, `direction=accumulating|reducing|new|exited`) and `search_insider_trades` (Form-4 transactions with SEC URLs) are available as signal inputs.
