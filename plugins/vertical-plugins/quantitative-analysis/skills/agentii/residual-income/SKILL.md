---
name: residual-income
multi_ticker_semantics: target_with_optional_peers
description: Residual Income valuation, EVA Economic Value Added, excess return valuation, book value plus economic profit, financial institution valuation, bank valuation, insurance company valuation
temporal_scope:
 default_quarters: 4
 max_quarters: 20
 description: "Trailing equity data; up to 20 quarters for projection"
allowed_tools:
 - search_xbrl_facts
 - get_realtime_quote
 - search_earnings_calendar
retrieval_scope: structured_only
min_tool_diversity: 3
---

# Residual Income / Economic Value Added (EVA) Valuation

Values a company as: Book Value + Present Value of Future Economic Profit. Economic profit = earnings ABOVE the required return on equity. Especially valuable for financial institutions (banks, insurers) where DCF is problematic due to the nature of debt (it's inventory, not capital) and for capital-intensive firms. Also known as the Edwards-Bell-Ohlson (EBO) model in academic literature.

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- residual income valuation {ticker}
- EVA valuation {ticker}
- economic value added {ticker}
- excess return model {ticker}
- book value plus economic profit {ticker}
- EBO model {ticker}
- bank valuation model {ticker}
- financial institution valuation {ticker}
- value {ticker} residual income
- RI valuation {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| projection_years | 5 | Years of explicit residual income forecast |
| terminal_growth | 2.5% | Perpetual RI growth (should be conservative) |
| cost_of_equity | CAPM | Ke = Rf + β × ERP, or manual input |

## Methodology

### Retrieval Scope

`structured_only` — Residual Income uses book value from XBRL + earnings estimates + current price.

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

### When to Use Residual Income vs. DCF

| Company Type | Preferred Model | Why |
|-------------|----------------|-----|
| Banks, Insurers | Residual Income | Debt is inventory, not capital — DCF doesn't work |
| Capital-Intensive Industrials | Residual Income | Asset-heavy; book value is meaningful |
| Asset Managers | Residual Income | AUM-based; book value + fee earnings |
| Tech, SaaS, Pharma | DCF | Asset-light; cash flow focus |
| Mature Dividend Payers | DDM | Dividends are the primary return mechanism |
| High-Growth, No Earnings | Revenue-based DCF | No earnings or book value to anchor |

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_residual-income_{affix}.md`.

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Validation Gates

1. **RI convergence**: residual income must not grow perpetually above Ke. *If failed*: terminal growth g must be < Ke by at least 2%.
2. **Book value consistency**: BV_t = BV_t-1 + NI_t - D_t must hold for all forecast years. *If failed*: refuse delivery; check arithmetic.
3. **Economic plausibility**: fair value P/B between 0.1x and 10x. *If failed*: flag extreme assumptions.

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
| Negative book value | Halt | "Book value is negative — Residual Income model not applicable. Use DCF." |
| No earnings data | Halt | "Insufficient earnings data for {ticker}." |
