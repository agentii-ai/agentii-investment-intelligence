---
name: business-model
multi_ticker_semantics: target_with_optional_peers
description: Business model classification, business model analysis, structural analysis of how a company makes money, product offering decomposition, distribution channel analysis, customer segment analysis, revenue model identification, market sizing TAM SAM SOM, competitive positioning, business unit performance, management team & leadership analysis, what does the company sell, how does the company go to market, business model type platform service product, channel mix direct vs indirect, revenue concentration risk, CEO CFO executive backgrounds and changes
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Structural analysis over a trailing 4 fiscal quarters (latest 10-K + trailing 10-Qs); max 8 for channel-mix or management-evolution windows. A single-quarter snapshot is INSUFFICIENT for business-model classification."
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - search_sec_filings
 - read_source_outline
 - read_source_deep_outline
 - read_source_pages
 - search_keyword_in_source
 - get_company_financials
 - get_company_profile
 - get_company_fiscal_calendar
 - get_ticker_coverage
 - list_xbrl_concepts
 - search_cross_period
 - batch_search
 - search_knowledge_entries
 - get_knowledge_entry
 - search_by_analogue
retrieval_scope: unstructured_document_search
min_tool_diversity: 9
---

<!-- analog: equity-research-core/business-model -->

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- analyze the business model of {ticker}
- run business model analysis on {ticker}
- decompose the business model of {ticker}
- what does {ticker} sell and how does it make money
- classify the business model type of {ticker}
- analyze {ticker} product offerings and distribution channels
- assess {ticker} revenue composition and concentration risk
- evaluate {ticker} TAM SAM SOM and market positioning
- analyze {ticker} management team and leadership changes
- review {ticker} go-to-market strategy
- breakdown {ticker} customer segments and distribution model
- structural analysis of {ticker}
- business unit performance analysis for {ticker}
- competitive positioning of {ticker}

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_quarters | 4 | Trailing 4 fiscal quarters (latest 10-K + trailing 10-Qs); a single-quarter snapshot is INSUFFICIENT for business-model classification |
| include_management_changes | true | Whether to surface leadership-change analysis (mode 1_5) |
| include_market_sizing | true | Whether to surface TAM/SAM/SOM (mode 1_4) |
| peer_set | none | Business-model analysis is single-issuer by default; peers are added by `/agentii:competitive` |

## Production Grounding

Production data-plane grounding (scale, locators) is in `references/methodology.md`.

## Data Source Priority (mandatory order)

1. **XBRL FIRST (grounding truth)** — `search_xbrl_facts` with the detailed/segment view for revenue & margins broken down by product line, segment, geography, and distribution channel (concepts `Revenues`, `GrossProfit`, `OperatingIncomeLoss`, `SegmentReportingInformation`). Retrieve XBRL BEFORE any document discovery.
2. **SEC filings** — `search_documents` / `search_sec_filings` for the 10-K (annual, richest business overview), trailing 10-Q, and 20-F for foreign issuers → `read_source_pages` enrichment.
3. **Web search = LAST RESORT** — only when SEC/XBRL coverage is genuinely insufficient (e.g., third-party TAM estimates, very recent unfiled events), and it MUST be flagged in Coverage Gaps. Web search is NOT an MCP tool and is never a substitute for filings.

## Methodology

### 1. Retrieval Scope

This skill performs **unstructured document search at scale** (10-K, 10-Q, 8-K filings and earnings call transcripts). The three-layer agent-use-ready retrieval protocol applies (Layer 1 → Layer 2 → Layer 3). For foreign issuers, use 20-F (annual) and 6-K (material events) instead of 10-K and 8-K respectively.

### 2. Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### 3. Temporal Scope

Default: 4 fiscal quarters (max 8). A single-quarter snapshot is INSUFFICIENT for business-model classification — use the latest 10-K (annual) plus trailing 10-Qs. Extend the window when explicitly tracking channel-mix evolution (mode 1_2 default 12 quarters) or management changes (mode 1_5 default 4 quarters).

### 4. Tool Allowlist

See frontmatter `allowed_tools`.

- `search_companies`, `get_company_profile` — issuer resolution and sector classification.
- `search_xbrl_facts`, `list_xbrl_concepts`, `get_company_financials` — segment-level P&L and revenue concentration metrics.
- `search_documents`, `search_sec_filings` — Layer 1 document discovery (with `secondary_labels` filter).
- `read_source_outline`, `read_source_pages`, `search_keyword_in_source` — Layer 2/3 deep read for business-overview pages.
- `get_company_fiscal_calendar`, `get_ticker_coverage` — pre-flight (mandatory first step).

### 5. Protocol

Step-by-step execution detail is in `references/methodology.md`.

**Moat Assessment**: When evaluating competitive advantage durability, apply the Sustainable Value Creation framework in `references/moat-methodology.md`. Quantify the ROIC−WACC spread magnitude, calibrate sustainability using sector-level ROIC autocorrelation data (Consumer Staples r=0.46 → Energy r=0.15), classify industry structure (Fragmented/Oligopoly/Dominant/Network/Commodity), and apply the 67-item Moat Checklist. High current ROIC in a rapid-mean-reversion industry is not a moat.

## Modes (5 — structural equity analysis)

This skill delivers analyst-grade output via 5 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Analyst Modes

This skill exposes addressable analysis modes (`--mode=<slug>` / `--modes=<s1>,<s2>` / `--mode=all`; see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The full mode definitions and their output templates live in `references/modes.md`. The default invocation runs the essentials subset.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_business-model_{affix}.md`.

**Output Directory Rule**: write to `{ticker}/` (e.g. `NVDA/`) — NEVER `{ticker}-recent-quarter/` or any dimension-suffixed variant. The directory is the bare uppercase ticker; the skill name appears only in the filename, never the directory.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Foreign issuer | `form_type=["10-K"]` empty | Retry with `form_type=["20-F"]` for annual + `form_type=["6-K"]` for material events | "Foreign issuer; using 20-F + 6-K instead of 10-K + 8-K." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile (skip channel-mix evolution) | "Limited historical data; mode 1_2 channel-mix trend skipped." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
