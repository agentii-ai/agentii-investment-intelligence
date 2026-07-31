---
name: chart-patterns
description: Chart pattern recognition, price action patterns, candlestick signal bars, pullback bar counting H1/H2/H3/H4, trend channels, micro channels, trading ranges, breakouts, major trend reversals 5-step sequence, wedges, double tops and bottoms, triangles, head and shoulders, climaxes, measured moves, support and resistance
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 1
  max_quarters: 4
  description: "Technical analysis pattern recognition operates on price data; 1 quarter default."
allowed_tools:
  - search_technical_setups
  - get_technical_setup
  - get_realtime_quote
retrieval_scope: structured_only
layer_tags: ["L4"]
min_tool_diversity: 2
parameter_free: false
---

> Methodology inspired by publicly taught price action trading frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| bar_count_threshold | 20 bars | Pullback > 20 bars = full Trading Range |
| reversal_steps | 5 | All trend reversals follow the same 5-step mechanical sequence |
| wedge_legs | 3 | Wedge requires three pushes at a trend extreme |
| climax_aftermath | Trading Range | After a climax, market enters TR before any reversal |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Chart patterns framework — `references/chart-patterns-reference.md` (bundled full pattern methodology)
2. Upstream context — market structure classification from `price-action` skill output
3. Technical setups — `search_technical_setups(pattern_type=..., market_condition=..., timeframe=...)` for matching against `gold.technical_setups`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: the pattern recognition framework is bundled in `references/chart-patterns-reference.md`. Real-time price data via `get_realtime_quote`. Matched technical setups via `search_technical_setups`. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements the price action trading pattern recognition framework: 17 distinct chart pattern types, each with specific identification criteria, decision rules, and entry/exit parameters. The core architecture: **Setup = Context + Signal Bar** — context (from `price-action` skill) determines which patterns are valid. A perfect signal bar in the wrong context is a losing trade. Detailed methodology and pattern-specific rules are in `references/chart-patterns-reference.md`.

#### Step 1 — Macro Context (Mode C — degrade-gracefully)

1. Assess VIX via `get_realtime_quote` for broad market proxy.
2. VIX elevated (> 25) → tighten position sizing, favor defined-risk setups. Low VIX (< 15) → standard sizing.
3. Degrade gracefully if unavailable: annotate `coverage_gap` and proceed.

#### Step 2 — Context from price-action Skill

Receive or derive market structure classification:
1. `market_condition`: trending_up / trending_down / ranging
2. `trend_strength`: strong / weak(channel) / none
3. `always_in_direction`: long / short / neutral
4. `cycle_phase`: breakout / channel / trading_range / reversal

**Critical rule**: Context determines which patterns are valid:
- Strong bull trend + always_in_long → only long patterns (H1, H2, bull breakouts). All short patterns invalid.
- Strong bear trend + always_in_short → only short patterns (L1, L2, bear breakouts).
- Ranging → Buy Low/Sell High only near boundaries. Middle of range = no trade.

#### Step 3 — Pattern Identification

Apply the full 17-pattern recognition framework based on current context:

**If in a Trend**:
1. **Pullback depth** → count legs: 1-leg = H1/L1 (strong trend), 2-leg = H2/L2 (channel), 3-leg = H3/L3 (broader), 4-leg = H4/L4 (near TR).
2. **Channel boundaries** → identify trend line and channel line. Assess tight vs broad.
3. **Breakout signals** → true vs false breakout assessment using bar characteristics.
4. **Reversal watch** → check if 5-step reversal sequence is progressing (Steps 1-5).

**If in a Trading Range**:
1. **Range boundaries** → identify support and resistance levels from prior swing points.
2. **Breakout preparation** → monitor for breakout direction.
3. **TR size assessment** → small TR (< 20 bars) = pullback, direction biased. Large TR (≥ 20 bars) = direction neutral.

**If near a Trend Extreme**:
1. **Climax check** → consecutive strong bars → sudden large counter-bar → climax detected. After climax: expect TR, not immediate reversal.
2. **Wedge check** → three pushes to same area, each push weaker → exhaustion signal.
3. **5-step reversal** → if Steps 1-4 are complete, watch for Step 5 confirmation.
4. **Double top/bottom** → two tests of same level; neckline break for confirmation.

#### Step 4 — Setup Matching via MCP

Match identified patterns against the `gold.technical_setups` database:

```
search_technical_setups(
  pattern_type=<pullback|breakout|reversal|trend_following|range_trading>,
  market_condition=<trending_up|trending_down|ranging>,
  timeframe=<derived from analysis>,
  instrument_scope=[<equity|option|futures>]
)
```

1. Filter results by `research_score` (higher = more thoroughly researched).
2. For each matched setup, load confirmation signals and compare against current market data.
3. Rank by fit: exact match → similar match → partial match.
4. If no match: proceed with manual pattern rules from `references/chart-patterns-reference.md`.

#### Step 5 — Pattern Output and Handoff

Produce structured pattern identification output:

1. **Primary pattern**: The best-fit identified pattern with confidence level.
2. **Secondary patterns**: Alternative patterns if primary is borderline.
3. **Invalid patterns**: Patterns that appear but are invalidated by context (e.g., bearish engulfing in strong bull).
4. **Handoff to `trade-execution`**: Pattern type + market condition + timeframe → for setup selection and trade plan generation.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_chart-patterns_{affix}.md`

## Output Structure

1. **Executive Summary** — Primary pattern identified, market context, confidence level
2. **Context Assessment** — Market structure (from price-action), Always In direction, valid/invalid pattern directions
3. **Trend Analysis** — Bar counting (H1/H2/H3/H4 status), channel classification (tight/broad), breakout quality
4. **Reversal Assessment** — 5-step sequence status (which steps have completed), climax detection, wedge count
5. **Pattern Details** — Primary pattern with specific entry/stop criteria, secondary patterns
6. **Setup Matches** — Results from `search_technical_setups` ranked by fit; match quality assessment
7. **Handoff Parameters** — pattern_type + market_condition + timeframe for trade-execution skill
8. **Coverage Gaps** — Data limitations and degraded-mode annotations

## Error Handling

| Error | Fallback |
|-------|----------|
| No upstream context from price-action | Self-derive market structure from raw price data; flag degraded |
| `search_technical_setups` unreachable | Provide manual pattern rules from references/chart-patterns-reference.md; flag gap |
| Pattern ambiguous | List all viable patterns; recommend waiting for confirmation bar |
| No matching pattern found | Report "no high-confidence pattern identified"; flag for manual review |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/chart-patterns-reference.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`