# Chart Patterns — Knowledge Base Integration

This skill identifies and interprets 17 chart pattern categories. The structured knowledge base provides detailed entry/exit rules for each pattern type.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `search_technical_setups` | Find setups by pattern_type, timeframe, market_condition |
| `get_technical_setup` | Full detail: entry trigger, confirmation signals, exit rules, invalidation, edge rationale |
| `search_by_analogue` | Cross-cutting search for historical pattern examples |

## Pattern Type Coverage (686 setups)

| pattern_type | Count | Pattern Examples |
|-------------|:-----:|-----------------|
| reversal | 138 | Double tops/bottoms, MTR, climax reversals, wedge reversals, head and shoulders |
| pullback | 85 | High/Low 1-4 pullbacks, bar counting entries, EMA pullbacks, flag patterns |
| trend_following | 81 | Always-In direction, swing entries, momentum continuation |
| market_structure | 66 | Bull/bear channels, micro channels, trading range boundaries |
| breakout | 58 | Breakout entries, gap open setups, opening range breakouts |
| support_resistance | 49 | Prior high/low as support/resistance, swing point tests |
| volatility_expansion | 32 | Straddle/strangle execution, VIX spike hedging |
| breakdown | 26 | Bear trend entries, failed support breaks |
| mean_reversion | 19 | RSI oversold/overbought, Bollinger Band touches |
| candlestick_pattern | 16 | Signal bars, engulfing patterns, bar counting |
| volatility_contraction | 9 | VCP pattern, tight ranges, dry-up in volume |
| consolidation | 4 | Range compression before expansion |
| moving_average | 6 | 20/50/200-period MA pullback entries |
| order_flow | 6 | Program trading detection, institutional footprints |
| gap | — | (subset of breakout) |

## Retrieval Strategy

1. **Identify pattern category** from chart analysis
2. **Search by pattern_type** to find all matching setups
3. **Filter by timeframe and market_condition** to match current context
4. **Get full detail** for top 3-5 matches to extract specific entry/exit rules
5. **Cross-reference** with `search_by_analogue` to find historical cases demonstrating the pattern

## Example Queries

```
# Find all reversal patterns for swing trading in bear trends
search_technical_setups(pattern_type="reversal", timeframe="swing", market_condition="trending_down")

# Find breakout setups for intraday
search_technical_setups(pattern_type="breakout", timeframe="intraday", market_condition="any")

# Get full detail including edge rationale and win rate context
get_technical_setup(setup_id="ts_double_top_bear_flag_forming_lower_high_major_trend_reversal")
```
