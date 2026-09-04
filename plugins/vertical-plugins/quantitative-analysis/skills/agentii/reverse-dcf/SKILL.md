---
name: reverse-dcf
multi_ticker_semantics: target_with_optional_peers
description: Reverse DCF valuation, implied growth rate, market expectations analysis, reverse discounted cash flow, implied valuation assumptions, market-implied projections, DCF sanity check
temporal_scope:
 default_quarters: 4
 max_quarters: 12
 description: "Current price input; historical data for comparison"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Reverse DCF — Market-Implied Expectations

Starts from the current stock price and solves backward: "What growth rate, margin, or WACC does the market currently price in?" Answers: "Is the market too optimistic or too pessimistic about {ticker}?" This is a sanity-check tool used by professional analysts to test whether consensus assumptions are already reflected in the stock price.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- reverse DCF {ticker}
- implied growth rate {ticker}
- what does the market price in {ticker}
- market-implied valuation {ticker}
- reverse discounted cash flow {ticker}
- is {ticker} priced for perfection
- market expectations DCF {ticker}
- sanity check valuation {ticker}
- implied assumptions {ticker}
- DCF reverse engineer {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| projection_years | 5 | Explicit forecast period |
| solve_for | growth_rate | growth_rate, terminal_margin, or wacc |
| terminal_growth | 2.5% | Long-term GDP-like growth rate |
| compare_to | consensus | Compare implied to consensus estimates |

## Methodology

### Retrieval Scope

`structured_only` — Reverse DCF uses current price + XBRL financials + consensus estimates.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default lookback: 4 fiscal quarter(s); maximum: 12. The default balances recency against the trend window this analysis requires.

### Tool Allowlist

Per frontmatter `allowed_tools`:

- `search_xbrl_facts` — primary structured financial facts (is_primary default)
- `get_realtime_quote` — latest market price for valuation cross-checks
- `search_earnings_calendar` — EPS actual/estimate/surprise + report dates

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

**Reverse DCF & PVGO**: When quantifying expectations embedded in the current stock price, apply the methodology in `references/reverse-dcf-methodology.md`. Solve for implied growth/WACC/margin assumptions, decompose enterprise value into Steady-State Value vs. PVGO, and apply the One Job expectations gap framework to structure the variant view. The Reverse DCF is an expectations diagnostic, not a valuation tool.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_reverse-dcf_{affix}.md`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Validation Gates

1. **Convergence**: DCF must converge to market price within 1% within 50 iterations. *If failed*: flag "DCF does not converge — extreme assumptions required."
2. **Economic plausibility**: implied growth rate must be between -10% and +50%. *If failed*: flag "Implied growth outside economically plausible range — market may be pricing non-fundamental factors."

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
| No price data | Halt | "Current stock price unavailable for {ticker}." |
| Negative FCF | Flag — reverse DCF unreliable | "Negative free cash flow — reverse DCF may produce nonsensical results." |
| Non-convergence | Flag extreme assumptions required | "Reverse DCF did not converge within 50 iterations — market may be pricing extreme scenarios." |
