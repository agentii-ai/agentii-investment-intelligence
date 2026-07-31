---
name: trade-execution
description: Trade execution using price action setups, major trend reversal trading top and bottom, MTR failure continuation, strong bull and bear breakout trading, strong and weak channel trading strategies, trading range strategies, opening range swings, integration with gold.technical_setups for setup matching and execution planning
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 1
  max_quarters: 4
  description: "Technical trade execution operates on price data; 1 quarter default."
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
| swing_reward_min | 2x risk | Swing trades require minimum 2:1 reward-to-risk |
| scalp_reward | 1x risk | Scalp trades take profits at 1:1 reward-to-risk |
| default_position_risk | 1-2% of capital | Standard risk per trade |
| mtr_failure_priority | highest | MTR failure is the strongest continuation signal |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Trade execution framework — `references/execution-scenarios.md` (bundled full execution methodology)
2. Pattern context — from `chart-patterns` skill output (pattern_type, market_condition, timeframe)
3. Market structure — from `price-action` skill output (Always In direction, trend strength)
4. Technical setups — `search_technical_setups` + `get_technical_setup` for exact entry/exit parameters from `gold.technical_setups`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: the execution framework is bundled in `references/execution-scenarios.md`. Real-time price data via `get_realtime_quote`. Matched technical setups via `search_technical_setups` and `get_technical_setup` for detailed execution parameters. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements the price action trading trade execution framework: 12 distinct trading scenarios with specific entry, stop, target, and invalidation rules. The core insight: **MTR failures produce the strongest continuation signals.** Detailed methodology, setup-specific rules, and the full setup→strategy matrix are in `references/execution-scenarios.md`.

This skill follows the **Mode C (Execution-Focused)** retrieval arc per spec 039 Part V.

#### Step 1 — Macro Context (degrade-gracefully)

1. Query `get_realtime_quote` for broad market proxy to assess VIX.
2. VIX > 25 → tighten position sizing (0.5-1% risk per trade), favor defined-risk setups.
3. VIX < 15 → standard sizing (1-2% risk per trade).
4. Macro regime from upstream analysis: expansion favors long setups, contraction favors shorts.

#### Step 2 — Thesis Input

Receive directional thesis from upstream skills:
1. From `price-action`: Always In direction, market condition, trend strength.
2. From `chart-patterns`: Primary pattern type, pattern confidence, secondary patterns.
3. Optional: user-provided thesis direction from fundamental analysis (L2+3 skills).
4. **Conflict resolution**: If fundamental thesis conflicts with technical structure, note the divergence and flag for review. Technical structure takes precedence for entry timing.

#### Step 3 — Setup Selection via MCP (framework-guided)

Match the identified pattern and market condition against `gold.technical_setups`:

```
search_technical_setups(
  pattern_type=<pullback|breakout|reversal|trend_following|range_trading>,
  market_condition=<trending_up|trending_down|ranging>,
  timeframe=<derived from time horizon>,
  instrument_scope=[<equity|option|futures>]
)
```

1. **Filter and rank**: Sort by `research_score` descending. Higher score = more thoroughly researched setup.
2. **Load full setup**: `get_technical_setup(setup_id=<best_match>)` to retrieve complete rules.
3. **Validate against context**: Does the setup's `market_condition` and `pattern_type` match the current analysis?
4. **Fallback**: If no matching setup, use manual execution rules from `references/execution-scenarios.md`. Flag as `coverage_gap`.

#### Step 4 — Execution Plan Construction

Build a complete trade plan by merging methodology with the matched setup's parameters.

**Entry specification**:
- Exact entry trigger: e.g., "Buy stop at $X (1 tick above signal bar high)"
- Alternative entry: e.g., "Or buy market if next bar confirms with strong close"
- MTR failure special case: "Enter market immediately on break back through trend line"

**Stop placement**:
- Primary rule: 1 tick beyond the opposite extreme of the signal bar
- MTR trades: beyond the most recent swing high/low
- Breakout trades: below/above the breakout point
- Adjust stop width to position size: wider stop = smaller size

**Profit targets**:
- Scalp target 1: 1x risk → partial position exit
- Swing target 2: 2x risk or measured move projection → remaining position exit
- Trailing stop: move stop to breakeven after scalp target reached

**Position sizing**:
- Risk per trade = account_risk_pct × capital
- Position size = risk_per_trade / (entry - stop)
- Adjust for VIX: higher VIX → smaller size
- Adjust for setup confidence: higher research_score → larger size (within limits)

**Invalidation conditions**:
- Price closes beyond stop before entry triggers
- Signal bar extreme is violated before the entry bar confirms
- Market context changes (trend breaks, TR forms) before entry
- MTR failure: price resumes reversal instead of continuing

#### Step 5 — Trade Plan Output

Produce the final executable trade plan:

1. **Setup Summary**: Setup name (from MCP), pattern type, confidence level (research_score).
2. **Direction**: Long / Short, Always In alignment.
3. **Entry Plan**: Exact trigger price, alternative entry method, optimal entry window.
4. **Stop Plan**: Exact stop price, stop rationale (which swing point / bar extreme), maximum dollar risk.
5. **Target Plan**: Target 1 (scalp) price and size, Target 2 (swing) price and size, trailing methodology.
6. **Position Size**: Shares/contracts calculated from risk parameters.
7. **Invalidation**: Specific conditions that void the trade before entry.
8. **Post-Entry Management**: When to move stop to breakeven, when to trail, when to exit early.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_trade-execution_{affix}.md`

## Output Structure

1. **Executive Summary** — Trade direction, setup name, key price levels, confidence
2. **Context Synthesis** — Market structure (price-action), identified pattern (chart-patterns), macro overlay
3. **Setup Selection** — MCP search_technical_setups results, selected setup with research_score, match justification
4. **Entry Plan** — Exact entry trigger price, alternative entry, execution window, volume conditions
5. **Stop Plan** — Exact stop price, stop rationale (which rule applied), maximum dollar/percent risk
6. **Target Plan** — Target 1 (scalp) price and percentage of position, Target 2 (swing) price and percentage, measured move reference
7. **Position Sizing** — Calculated position size, risk per share, total position risk
8. **Invalidation** — Pre-entry invalidation conditions, post-entry stop management rules
9. **Coverage Gaps** — Any data limitations, degraded-mode parameters, setup match caveats

## Error Handling

| Error | Fallback |
|-------|----------|
| No matching setup from MCP | Use manual execution rules from references/execution-scenarios.md; flag coverage_gap |
| `search_technical_setups` unreachable | Proceed with manual rules only; flag all parameters as manually derived |
| Pattern confidence low | Reduce position size by 50%; flag as lower-confidence trade |
| Conflicting upstream signals | Hold; do not trade. Flag conflict for manual review |
| No context from upstream skills | Derive market structure from raw price data where possible; flag degraded |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs referencing the matched `gold.technical_setups` entries.

## References

- `references/execution-scenarios.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`