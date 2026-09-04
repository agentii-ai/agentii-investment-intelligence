---
name: ratio-analysis
multi_ticker_semantics: target_with_optional_peers
description: Financial ratio analysis, profitability ratios ROE ROA ROIC, liquidity ratios current quick cash, leverage ratios debt-to-equity interest coverage, efficiency ratios asset turnover inventory turnover DSO, valuation ratios PE PB EV/EBITDA, cross-company ratio comparison, DuPont analysis
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Trailing 4 quarters for current ratios, up to 12 for trend analysis"
allowed_tools:
 - get_financial_ratios
 - search_xbrl_facts
 - search_companies
 - get_realtime_quote
 - search_earnings_calendar
 - get_company_financials
 - batch_search
retrieval_scope: structured_only
min_tool_diversity: 7
---

# Financial Ratio Analysis

Quantitative skill computing 6 categories of financial ratios from XBRL financial data. Cross-company comparison within sector. References professional financial training ratio interpretation standards.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

**`get_realtime_quote` availability **: If `get_realtime_quote` is not yet deployed in the MCP surface, use `search_earnings_calendar` for PE/earnings data and flag valuation ratios as "current price unavailable — using latest reported data." Prompts user for current stock price as manual fallback.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- analyze financial ratios for {ticker}
- ratio analysis {ticker}
- compute profitability ratios {ticker}
- liquidity analysis {ticker}
- leverage analysis {ticker}
- efficiency ratios {ticker}
- valuation ratios {ticker}
- DuPont analysis {ticker}
- cross-company ratio comparison {ticker}
- compare {ticker} ratios to peers

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| lookback_quarters | 4 | Trailing 4 quarters for current ratios |
| include_peers | true | Cross-company comparison within sector |
| ratio_categories | all | profitability, liquidity, leverage, efficiency, valuation, growth |

## Methodology

### Retrieval Scope

`structured_only` — this skill computes ratios from XBRL financial data and real-time price data. No unstructured document search required. All data sources are queryable via agentii MCP tools.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default: 4 fiscal quarters (max 12). Ratio analysis uses trailing 4 quarters for current snapshot; up to 12 quarters for trend analysis.

### Tool Allowlist

See frontmatter `allowed_tools`. `search_xbrl_facts` is the primary data source for financial statement line items. `get_realtime_quote` provides current stock price for valuation ratios (P/E, P/B, P/S). `search_companies` enables peer identification for cross-company comparison.

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

**ROIC Analysis**: When computing Return on Invested Capital, apply the institutional-grade framework in `references/roic-methodology.md`. Use the four-variant approach (excluding/including goodwill × with/without intangible capitalization) appropriate to the analytical question, industry-specific capitalization rates per the academic framework, ROIIC over rolling 3-year periods, and DuPont decomposition to map ROIC to competitive strategy. Is the company passing the one dollar test?

### Ratio Definitions

Full ratio formula definitions are in `references/methodology.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_ratio-analysis_{affix}.md` . Example affixes: `profitability`, `liquidity-leverage`, `peer-comparison`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

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
| Missing data | XBRL returns empty for key concepts | Widen date range and retry once | "No financial data available for {ticker} in requested window." |
| Non-USD currency | `unit` field is not USD | Annotate with ISO 4217 code | "⚠ {ticker} reports in {currency}. Ratios computed in reporting currency." |
| Peer data incomplete | <3 peers have comparable data | Reduce peer set; flag incomplete peers | "Cross-company comparison based on {n} of {m} peers with complete data." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
