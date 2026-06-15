---
name: peg-valuation
multi_ticker_semantics: target_with_optional_peers
description: PEG valuation, Price Earnings to Growth ratio, Peter Lynch PEG methodology, growth-adjusted valuation, earnings growth rate, PE ratio valuation, PEG sector comparison, undervalued growth stocks, fair value PEG
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Trailing 4 quarters for current PE; up to 12 for historical CAGR"
allowed_tools:
 - search_xbrl_facts
 - search_companies
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 4
---

# PEG Valuation

Peter Lynch PEG (Price/Earnings to Growth) methodology. PEG = P/E Ratio ÷ Earnings Growth Rate (%). Growth-adjusted valuation that answers: "Is this stock's growth justifying its multiple?"

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

**`get_realtime_quote` availability **: If `get_realtime_quote` is not yet deployed, prompt user for current stock price. PE numerator from `search_earnings_calendar` (NTM consensus EPS × current price = PE) as fallback.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- PEG valuation for {ticker}
- compute PEG ratio {ticker}
- Peter Lynch PEG {ticker}
- growth-adjusted valuation {ticker}
- is {ticker} undervalued by PEG
- PEG analysis {ticker}
- price earnings growth {ticker}
- compare PEG across peers
- {ticker} PEG vs sector
- growth at reasonable price {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| growth_source | consensus | consensus estimates preferred; fallback to historical CAGR |
| include_peers | true | Sector PEG comparison |
| lookback_years | 3 | Historical CAGR computation window |

## Methodology

### Retrieval Scope

`structured_only` — PEG uses XBRL earnings data + real-time price + earnings calendar for growth estimates.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default: 4 fiscal quarters (max 12). PEG uses trailing 4 quarters for LTM P/E; up to 12 for historical EPS CAGR if consensus unavailable.

### Tool Allowlist

See frontmatter `allowed_tools` — 4 tools. `get_realtime_quote` for current price + PE (TTM). `search_earnings_calendar` for consensus EPS and long-term growth estimates. `search_xbrl_facts` for historical EPS to compute CAGR. `search_companies` for peer identification.

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

### PEG Interpretation (Peter Lynch Framework)

| PEG Range | Rating | Investment Implication |
|-----------|--------|----------------------|
| < 0.5 | Deeply Undervalued | Growth vastly exceeds valuation; investigate for hidden risks |
| 0.5 – 1.0 | Undervalued | Classic Lynch buy zone; growth justifies the multiple |
| 1.0 – 1.5 | Fairly Valued | Growth and valuation in equilibrium |
| 1.5 – 2.0 | Premium | Market paying up for growth; needs above-consensus execution |
| > 2.0 | Overvalued | Growth insufficient to justify current multiple |
| Negative | N/A | Negative earnings — PEG not meaningful; use revenue-based metrics |

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_peg-valuation_{affix}.md`.

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
| Missing data | No consensus or historical EPS | Halt; cannot compute growth rate | "Insufficient earnings data to compute growth rate for {ticker}." |
| Negative earnings | PE (TTM) < 0 | Compute only revenue-based metrics; flag PEG as N/A | "PEG not applicable — {ticker} has negative earnings." |
| Zero growth | CAGR ≈ 0% | PEG = ∞; flag as "no growth" case | "Zero historical EPS growth — PEG effectively infinite." |
| MCP unreachable | Preflight probe fails | Halt | "agentii data plane unreachable; check connection." |
