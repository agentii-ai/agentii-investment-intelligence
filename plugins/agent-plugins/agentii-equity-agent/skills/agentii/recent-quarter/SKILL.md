---
name: recent-quarter
multi_ticker_semantics: single_target
description: Recent quarter performance analysis, quarterly earnings review, last quarter results, quarterly financial performance, analyze recent quarter, Q4 earnings, quarterly revenue breakdown, EPS this quarter, margin analysis recent quarter, sequential growth, quarterly performance review
temporal_scope:
 default_quarters: 1
 max_quarters: 4
 description: "Recent quarter analysis focuses on the most recent quarter's P&L. Max 4 quarters for sequential trend."
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - get_company_financials
 - get_company_profile
 - search_earnings_calendar
 - get_company_fiscal_calendar
 - get_ticker_coverage
 - list_xbrl_concepts
 - batch_search
retrieval_scope: structured_only
min_tool_diversity: 6
---

# Recent Quarter Performance

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- analyze recent quarter performance for {ticker}
- quarterly earnings review for {ticker}
- last quarter results {ticker}
- quarterly financial performance {ticker}
- analyze {ticker} recent quarter
- {ticker} Q4 earnings
- {ticker} quarterly revenue breakdown
- EPS this quarter {ticker}
- margin analysis recent quarter {ticker}
- sequential growth {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| lookback_quarters | 1 | Single most-recent quarter |
| include_sequential | true | Show QoQ growth rates |

## Methodology

### 1. Retrieval Scope

This skill performs **structured data retrieval only** (XBRL facts + earnings calendar). No unstructured document search — business-model structural analysis is handled by `/agentii:business-model` . This skill is TEMPORAL/QUANTITATIVE .

### 2. Retrieval Strategy

1. ** Pre-flight (mandatory)**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`. Route based on coverage.
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest])` — returns `is_primary: true` rows by default.
3. **Earnings calendar**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])` — returns EPS actual/estimate/surprise. Use `get_company_fiscal_calendar` for fiscal period orientation, NOT `search_earnings_calendar` .
4. **Consolidated P&L**: `get_company_financials/{ticker}` returns IS/BS/CF highlights with XBRL data.

### 3. Temporal Scope

Default: 1 fiscal quarter (max 4). This skill is a temporal snapshot of the most recent quarter's financial performance.

### 4. Tool Allowlist

See frontmatter `allowed_tools`. This skill is `structured_only` (temporal/quantitative only). `search_xbrl_facts` is the primary data source for consolidated P&L metrics. `search_earnings_calendar` provides EPS actuals, estimates, and surprise data. `get_company_fiscal_calendar` resolves fiscal period orientation. Document search and structural analysis belong to `/agentii:business-model` .

### 5. Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format, then `get_ticker_coverage/{ticker}` .
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest])` — returns `is_primary: true` rows by default.
3. **Earnings calendar**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])` for EPS actuals, estimates, and surprise percentages.
4. **Financial highlights**: `get_company_financials/{ticker}` for IS/BS/CF summary data.
5. **Output**: produce P&L progression table with QoQ and YoY growth rates, margin trend chart data, and earnings-vs-consensus comparison.

## Modes (5 — temporal / quantitative)

**This skill is temporal/quantitative ONLY.** Structural analysis (business model classification, product-line decomposition, channel analysis) belongs to `/agentii:business-model` . Modes below focus on quarterly P&L data, growth rates, margins, and earnings vs. consensus.

### Analyst Modes

This skill exposes addressable analysis modes (`--mode=<slug>` / `--modes=<s1>,<s2>` / `--mode=all`; see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The full mode definitions and their output templates live in `references/modes.md`. The default invocation runs the essentials subset.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_recent-quarter_{affix}.md` . Example affixes: `consolidated-p-and-l`, `margin-trends`, `earnings-vs-consensus`.

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
|-------------|-----------|--------|---------------------|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
