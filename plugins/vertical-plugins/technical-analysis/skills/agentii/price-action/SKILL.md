---
name: price-action
description: Price action market structure analysis, trend vs trading range classification, Always In directional framework, buying/selling pressure analysis, market cycle phase identification, the price action methodology
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 1
  max_quarters: 4
  description: "Technical analysis operates on price data; 1 quarter default for short-to-medium-term setups."
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
| trend_confirmation_bars | 3 | Minimum consecutive bars for trend confirmation |
| trading_range_threshold | 20 bars | Pullback > 20 bars becomes a full Trading Range |
| reversal_failure_rate | 80% | In a trending market, ~80% of reversal attempts fail and become flags |
| inertia_rule | 60-40 | 60% probability trend continues, 40% probability reversal |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Price action framework — `references/market-structure.md` (bundled market structure methodology)
2. Real-time price data — `get_realtime_quote` for OHLCV and VIX context
3. Technical setups — `search_technical_setups` for matching pattern setups

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: the methodology framework is bundled in `references/market-structure.md`. Real-time price data supplements via `get_realtime_quote`. Matched technical setups via `search_technical_setups(market_condition=...)`. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements the price action trading framework: market structure analysis using price action alone — no indicators except a 20-bar EMA. The core thesis: **every market is always in one of two states — Trend or Trading Range. If uncertain, it is a Trading Range.** Detailed methodology, definitions, and decision rules are in `references/market-structure.md`.

#### Step 1 — Macro Context (Mode C — degrade-gracefully)

Assess the broader market environment before analyzing individual setups.

1. Query `get_realtime_quote` for a broad market proxy (SPY/SPX) to assess VIX levels.
2. Determine the macro regime from upstream analysis (expansion/contraction/stagflation/recovery).
3. VIX assessment: elevated (> 25) → tighten position sizing, favor defined-risk setups. Low (< 15) → standard sizing.

#### Step 2 — Market Structure Identification

Answer the most important question in price action: **Trend or Trading Range?**

1. **Cycle Phase Identification**:
   - Trend = Series of higher highs/lows (bull) or lower highs/lows (bear). Contains breakout→channel sub-phases.
   - Trading Range = Sideways movement. ≥ 20 bars = full TR. < 20 bars within a trend = Pullback.
   - Reversal Signal = Trading Range at a trend extreme that transitions into opposite trend.
2. **Trend Strength Classification**:
   - **Strong Trend (Breakout/Spike)**: Big bodies, small tails, consecutive bars with little overlap.
   - **Weak Trend (Channel)**: Bars with visible tails and overlap, contained between two parallel lines.
3. **Pullback vs Trading Range Rule**:
   - Pullback = < 20 bars pause; breakout likely in trend direction.
   - Trading Range = ≥ 20 bars; direction lost; breakout equally likely either way.
   - Fractal check: what appears as a pullback on this timeframe may be a trading range on a lower timeframe.

#### Step 3 — Directional Bias

Determine the directional bias using the Always In framework.

1. **Ask**: "If forced to enter the market right now, long or short?" Your answer = Always In direction.
2. **If unclear**: the market is in a Trading Range. Confusion = hallmark of TR.
3. **Directional bias rules**:
   - Always In Long → only consider long setups; ignore short signals even if they look strong.
   - Always In Short → only consider short setups; ignore long signals.
   - No clear Always In → Trading Range mode: Buy Low, Sell High, scalp only.

#### Step 4 — Pressure Analysis

Identify which side (bulls/bears) is applying dominant pressure.

1. **Bar-by-bar assessment**:
   - Close near high = bulls dominated through bar's life.
   - Close near low = bears dominated.
   - Long tail above = bears aggressively sold higher prices → failed breakout upward.
   - Long tail below = bulls aggressively bought lower prices → failed breakout downward.
2. **Every tail is a failed breakout** — it was once a strong trend body that got reversed. Tails signal the failure of one side.
3. **Context override**: A small body in a strong trend behaves as a trend bar. A big body in a sideways market behaves as a trading range bar. Context always overrides individual bar appearance.

#### Step 5 — Momentum Assessment

Assess momentum using the 20-60 day framework: Technical Analysis (patterns/formations) provides the big picture over weeks to months. Price Action (momentum) provides the near-term directional signal over days to weeks. Both must align for a trade to have favorable timing.

1. **RSI (Relative Strength Index)** — 14-day and 20-day:
   - Above 70 = overbought; below 30 = oversold.
   - RSI reversing from overbought = momentum fading from the upward move.
   - Avoid entering longs when RSI is overbought and falling; avoid shorts when RSI is oversold and rising.
   - Treat "overbought" and "oversold" with caution: a strong trend can stay overbought/oversold for extended periods.

2. **Moving Averages** — SMA and EMA at 20, 60, 120, and 250 periods:
   - Price above rising MA = bullish momentum confirmed.
   - Price below falling MA = bearish momentum confirmed.
   - MA convergence/flattening = momentum weakening, potential transition.

3. **MACD (Moving Average Convergence Divergence)**:
   - Standard: (12, 26, 9). Extended: (20, 60, 10) and (20, 60, 20) for longer timeframes.
   - MACD line crossing above signal line = bullish momentum shift.
   - MACD line crossing below signal line = bearish momentum shift.
   - Divergence between MACD and price = potential reversal signal.

4. **Heikin Ashi Candles**: Use for smoothing price action and identifying sustained momentum. Consecutive Heikin Ashi bars without lower shadows = strong bull momentum. Without upper shadows = strong bear momentum.

5. **Timing Assessment (Traffic-Light System)**:
   - Green: Market structure + momentum + Always In direction all aligned → favorable entry timing.
   - Amber: Partial alignment, some conflicting signals → caution; reduce position size or wait.
   - Red: Conflicting signals across structure/momentum/direction → do not enter; wait for clearer conditions.

#### Step 6 — Setup Context Handoff

Produce the market structure output to be consumed by downstream skills.

1. **Output classification**:
   - `market_condition`: `trending_up` / `trending_down` / `ranging`
   - `trend_strength`: `strong` / `weak` / `none`
   - `always_in_direction`: `long` / `short` / `neutral`
   - `cycle_phase`: `breakout` / `channel` / `trading_range` / `reversal`
2. **Handoff to `chart-patterns`**: The context above determines which patterns are valid. In a strong bull trend, only long patterns are valid — all short patterns are ignored regardless of how strong they appear.
3. **MCP retrieval**: `search_technical_setups(market_condition=<derived>)` for rough matching against `gold.technical_setups`.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_price-action_{affix}.md`

## Output Structure

1. **Executive Summary** — Market state (Trend/TR), Always In direction, cycle phase with confidence level
2. **Market Structure Analysis** — Trend strength, cycle phase, pullback vs trading range classification with specific bar counts
3. **Always In Assessment** — Directional bias, rationale, confidence level
4. **Pressure Analysis** — Bull/bear dominance assessment, key tail/bodie signals on recent bars
5. **Transition Signals** — Early warning signals of cycle phase change (channel flattening, TR forming at extreme)
6. **Pattern Context** — Valid pattern directions for downstream chart-patterns skill
7. **Coverage Gaps** — Data limitations and degraded-mode annotations

## Error Handling

| Error | Fallback |
|-------|----------|
| No price data available | Proceed with static market structure principles; flag degraded |
| `search_technical_setups` unreachable | Skip MCP step; provide manual pattern analysis |
| Ambiguous market state | Classify as Trading Range; note ambiguity |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/market-structure.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`
