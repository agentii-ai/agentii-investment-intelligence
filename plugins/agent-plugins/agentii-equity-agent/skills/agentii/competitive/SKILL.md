---
name: competitive
multi_ticker_semantics: target_with_required_peers
description: Competitive landscape analysis, competitor comparison, peer positioning, market share dynamics, competitive moat assessment, Porter five forces, industry competition, competitive advantage analysis, market positioning, strategic group mapping, compare competitors
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
 - list_coverage
 - search_earnings_calendar
 - get_company_profile
 - batch_search
 - read_source_outline
 - read_source_deep_outline
 - list_xbrl_concepts
 - read_source_pages
 - search_keyword_in_source
 - search_knowledge_entries
 - get_knowledge_entry
 - search_by_analogue
 - search_investment_cases
 - get_investment_case
retrieval_scope: unstructured_document_search
min_tool_diversity: 12
---

<!-- analog: sector-overview -->

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- analyze dim competitive landscape
- run dim competitive landscape analysis
- produce dim competitive landscape report
- dim competitive landscape breakdown
- dim competitive landscape deep dive
- build a dim competitive landscape
- assess dim competitive landscape
- quantify dim competitive landscape
- compare dim competitive landscape across peers
- review dim competitive landscape for
- generate dim competitive landscape on
- dim competitive landscape for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

<!-- BEGIN port-dimension-prompts methodology + modes -->

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings and earnings call transcripts spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_labels=material_definitive_agreement_1_01,other_events_8_01` to surface M&A / partnership / strategic-action 8-Ks before Layer 2.

### Temporal Scope

Default: 8 fiscal quarters (max 16). Competitive landscape: 8 quarters for market-share trajectories and positioning shifts

### Tool Allowlist

See frontmatter `allowed_tools`.

### Protocol

This skill delivers analyst-grade output via 8 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

**Industry Structure**: For the full moat assessment framework covering ROIC persistence by sector, Five Forces + Barriers integration, disruption analysis, and the 67-item Moat Checklist, consult `business-model/references/moat-methodology.md` — this skill uses the industry-level sections of that framework.

### Analyst Modes

This skill exposes addressable analysis modes (`--mode=<slug>` / `--modes=<s1>,<s2>` / `--mode=all`; see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The full mode definitions and their output templates live in `references/modes.md`. The default invocation runs the essentials subset.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_competitive_peer-positioning.md` .

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
