---
name: earnings-sentiment
multi_ticker_semantics: single_target
description: Earnings sentiment analysis, analyst estimates vs guidance, earnings surprise history, consensus sentiment, earnings revision trends, analyst rating changes, earnings beat miss track record, guidance accuracy, whisper numbers, pre-announcement sentiment
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - read_source_outline
 - read_source_deep_outline
 - read_source_pages
 - search_earnings_calendar
 - get_company_financials
 - get_company_profile
 - list_xbrl_concepts
 - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: catalyst-calendar -->

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- analyze dim earnings sentiment
- run dim earnings sentiment analysis
- produce dim earnings sentiment report
- dim earnings sentiment breakdown
- dim earnings sentiment deep dive
- build a dim earnings sentiment
- assess dim earnings sentiment
- quantify dim earnings sentiment
- compare dim earnings sentiment across peers
- review dim earnings sentiment for
- generate dim earnings sentiment on
- dim earnings sentiment for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

<!-- BEGIN port-dimension-prompts methodology + modes -->

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Earnings sentiment: trailing 4 quarters for earnings-call tone and guidance trends

### Tool Allowlist

See frontmatter `allowed_tools`.

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

### Analyst Modes

This skill exposes addressable analysis modes (`--mode=<slug>` / `--modes=<s1>,<s2>` / `--mode=all`; see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The full mode definitions and their output templates live in `references/modes.md`. The default invocation runs the essentials subset.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_earnings-sentiment_analyst-sentiment.md` .

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
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
