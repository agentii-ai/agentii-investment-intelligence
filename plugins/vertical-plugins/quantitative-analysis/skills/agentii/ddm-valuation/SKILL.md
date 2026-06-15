---
name: ddm-valuation
multi_ticker_semantics: target_with_optional_peers
description: Dividend Discount Model, DDM valuation, multi-stage dividend model, Gordon Growth Model, dividend growth valuation, mature company valuation, income stock valuation, dividend yield analysis
temporal_scope:
 default_quarters: 4
 max_quarters: 20
 description: "Dividend history requires 5+ years; forecast up to 10 years"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Dividend Discount Model (DDM)

Multi-stage DDM for mature dividend-paying companies. Values a stock as the present value of all expected future dividends. Especially appropriate for financials (JPM, BAC), utilities (DUK, SO), consumer staples (PG, KO), and REITs — where dividends are the primary mechanism of shareholder returns.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- dividend discount model {ticker}
- DDM valuation {ticker}
- dividend growth valuation {ticker}
- Gordon Growth Model {ticker}
- multi-stage DDM {ticker}
- income stock valuation {ticker}
- dividend yield analysis {ticker}
- value {ticker} by dividends
- mature company valuation {ticker}
- dividend-based fair value {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| stages | 3 | Explicit → Transition → Maturity |
| explicit_years | 5 | Years of explicit dividend forecast |
| transition_years | 5 | Years of declining growth |
| terminal_growth | 2.5% | Long-term perpetual growth (GDP proxy) |

## Methodology

### Retrieval Scope

`structured_only` — DDM uses dividend history from XBRL + current price + earnings estimates.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 20. The default balances recency against the trend window this analysis requires.

### Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `get_realtime_quote` — latest market price for valuation cross-checks
- `search_earnings_calendar` — EPS actual/estimate/surprise + report dates

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_ddm-valuation_{affix}.md`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Validation Gates

1. **Dividend consistency**: DPS must be positive in ≥4 of last 5 years. *If failed*: flag "Dividend history insufficient for reliable DDM — consider Residual Income or DCF."
2. **Growth sustainability**: DPS growth rate must not exceed sustainable growth rate (ROE × (1 - Payout Ratio). *If failed*: flag "Dividend growth exceeds sustainable rate — imply future dilution or leverage increase."
3. **Terminal value reasonableness**: Terminal value must be <80% of total fair value. *If failed*: flag "Terminal value dominates (>80% of fair value) — model highly sensitive to terminal assumptions."

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

| Failure Mode | Action | User-Facing Message |
|-------------|--------|---------------------|
| No dividend history | Halt; redirect to DCF or Residual Income | "{ticker} does not pay dividends — DDM not applicable. Use DCF or Residual Income." |
| Zero or negative beta | Prompt user for manual beta input | "Beta unavailable for {ticker}. Please provide beta estimate." |
