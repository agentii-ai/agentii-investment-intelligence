---
name: options-execution
description: Options trade execution, directional strategies long call covered call collar, spread strategies bull call bear put ratio ladder, volatility strategies straddle strangle strap strip, liquidity cost and implied volatility filters, integration with gold.technical_setups for options setup matching
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 1
  max_quarters: 4
  description: "Options execution operates on 30-90 day horizons; 1 quarter default."
allowed_tools:
  - search_technical_setups
  - get_technical_setup
  - get_realtime_quote
retrieval_scope: structured_only
layer_tags: ["L4"]
min_tool_diversity: 2
parameter_free: false
---

> Methodology fused from professional options trading frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| min_days_to_expiry | 45 | Buying strategies need time for thesis to develop |
| max_days_to_expiry_sell | 45 | Selling strategies capture theta decay in 30-45 day window |
| exit_dte_threshold | 21 | Exit or roll buying strategies before 21 DTE to avoid gamma risk |
| bid_ask_max_spread | 5% | Illiquid options destroy edge through wide spreads |
| max_position_risk | 2% | Maximum capital risk per single options trade |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Options execution framework — `references/options-strategies.md` (bundled strategy reference)
2. Upstream context — market structure from `price-action` + pattern identification from `chart-patterns`
3. Options setups — `search_technical_setups(instrument_scope=["option"], ...)` for matching against `gold.technical_setups`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: the strategy framework is bundled in `references/options-strategies.md`. Real-time data via `get_realtime_quote`. Matched options setups via `search_technical_setups(instrument_scope=["option"])`. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements a professional options execution framework. Options are treated as execution tools for expressing directional or volatility views with defined risk — not as standalone gambling instruments. The framework applies three mandatory filters (liquidity, cost, volatility) before any strategy selection. Detailed strategy definitions, the strategy→market condition matrix, and execution rules are in `references/options-strategies.md`.

#### Step 1 — Macro and Volatility Context

1. Assess broad market volatility via VIX or equivalent from `get_realtime_quote`.
2. Classify IV environment: High IV (> 70th percentile) → favor premium-selling strategies. Low IV (< 30th percentile) → favor premium-buying strategies. Mid-range → balanced.
3. Macro regime from upstream analysis: expansion favors longs, contraction favors shorts; high uncertainty favors straddle/strangle.

#### Step 2 — Directional Thesis Input

1. Receive Always In direction from `price-action` skill.
2. Receive primary pattern and confidence level from `chart-patterns` skill.
3. If no upstream context: derive from raw price data and fundamental thesis.
4. Classify thesis: Bullish / Bearish / Neutral / Direction-uncertain-large-move-expected.

#### Step 3 — Strategy Selection

Apply the strategy matrix to select the appropriate options structure:

1. **Apply filters**: Check liquidity (bid-ask spread), cost (premium vs position), IV environment.
2. **Map thesis to strategy**: Use the strategy→condition matrix in `references/options-strategies.md`.
3. **Query pipeline setups**: `search_technical_setups(instrument_scope=["option"], pattern_type=<derived>)` for matching strategy setups from `gold.technical_setups`.
4. **Load full setup**: `get_technical_setup(setup_id=<best_match>)` for exact parameters.
5. **Fallback**: Use manual strategy rules from the reference.

#### Step 4 — Execution Plan

1. **Strike selection**: OTM for directional (delta 0.40-0.60), ATM for straddles, OTM for strangles.
2. **Expiry selection**: 45-60 DTE for buying strategies, 30-45 DTE for selling strategies.
3. **Position sizing**: Risk/contract ≤ 2% of capital. For selling strategies, size on notional exposure.
4. **Exit plan**: Profit target, time stop (21 DTE for buys), stop loss level.
5. **Invalidation**: Conditions that void the trade (thesis break, IV regime change, liquidity deterioration).

#### Step 5 — Trade Plan Output

1. **Strategy**: Selected options strategy with justification from the matrix.
2. **Contract Specs**: Strike(s), expiry, type (call/put), net debit/credit.
3. **Risk**: Maximum loss in dollars and percentage of capital.
4. **Reward**: Target profit, probability of profit (if calculable).
5. **Breakeven**: Exact breakeven price(s) at expiration.
6. **Management Plan**: Roll/adjust/exit conditions.
7. **Setup Match**: If from `gold.technical_setups`, include setup_id and research_score.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_options-execution_{affix}.md`

## Output Structure

1. **Executive Summary** — Selected strategy, market conditions, thesis alignment, key contract specs
2. **Volatility Context** — IV percentile, IV environment classification, implications for strategy selection
3. **Directional Thesis** — Price-action derived view, pattern context, confidence level
4. **Filter Results** — Liquidity check (bid-ask), cost assessment, IV filter outcome
5. **Strategy Selection** — Strategy matrix match, pipeline setup match (if any), justification
6. **Contract Specifications** — Exact strikes, expiry, premiums, net debit/credit
7. **Risk and Reward** — Max loss, max profit, breakeven(s), probability assessment
8. **Management Plan** — Entry timing, profit targets, time stop, adjustment triggers
9. **Coverage Gaps** — Data limitations, manual vs pipeline-derived parameters

## Error Handling

| Error | Fallback |
|-------|----------|
| No matching options setup from MCP | Use manual strategy rules from references/options-strategies.md; flag coverage_gap |
| IV data unavailable | Assume mid-range IV; flag as degraded |
| Bid-ask wider than 5% | Flag as low-liquidity; suggest alternative strikes or skip |
| No directional thesis from upstream | Derive from raw price data; flag as independently determined |
| `search_technical_setups` unreachable | Use full manual strategy matrix; flag all parameters |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs referencing matched `gold.technical_setups` entries.

## References

- `references/options-strategies.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`