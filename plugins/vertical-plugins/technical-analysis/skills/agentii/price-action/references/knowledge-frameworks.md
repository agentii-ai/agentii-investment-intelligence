# Price Action — Knowledge Base Integration

This skill is powered by a structured knowledge base of institutional-grade technical execution setups, investment strategies, and historical cases. Use the MCP tools below to retrieve relevant data.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `search_technical_setups` | Find setups by pattern_type, timeframe, market_condition, practitioner |
| `get_technical_setup` | Full detail for a specific setup (entry, exit, invalidation, edge) |
| `search_by_analogue` | Cross-cutting search: "what historical situations match this market regime?" |

## Available Data

- **686 technical setups** in `gold.technical_setups` covering 15 pattern types across 4 trading courses
- **659 investment strategies** in `gold.investment_strategies` from institutional funds and independent research
- **1341 investment cases** in `gold.investment_cases` — structured historical episodes

## Retrieval Strategy for Price Action

1. **Market structure assessment**: Search setups by `market_condition` (trending_up/trending_down/ranging/volatile)
2. **Directional bias**: Filter by `pattern_type` matching the identified market phase
3. **Setup selection**: Use `get_technical_setup` for detailed entry/exit rules on top matches
4. **Context enrichment**: Call `search_by_analogue(market_regime=...)` to find historical cases with similar market conditions

## Key Setup Categories for Price Action

| pattern_type | Count | When to Use |
|-------------|:-----:|-------------|
| reversal | 138 | Trend exhaustion, climax patterns, MTR setups |
| pullback | 85 | Trend continuation entries, flag patterns |
| trend_following | 81 | Always-In direction, momentum entries |
| market_structure | 66 | Channel trading, support/resistance |
| breakout | 58 | Breakout entries, gap setups |
| support_resistance | 49 | Range trading, swing points |
| volatility_expansion | 32 | Options straddle/strangle execution |
| breakdown | 26 | Bear trend entries, short setups |
| mean_reversion | 19 | Oversold/overbought fades |
| candlestick_pattern | 16 | Bar counting, signal bars |
| volatility_contraction | 9 | VCP, tight ranges before expansion |
| order_flow | 6 | Program trading, institutional footprints |
| moving_average | 6 | MA pullback entries |
| consolidation | 4 | Range compression setups |

## Example Queries

```
# Find pullback entries for bull trends
search_technical_setups(pattern_type="pullback", market_condition="trending_up")

# Find reversal setups for volatile markets  
search_technical_setups(pattern_type="reversal", market_condition="volatile")

# Cross-reference with historical cases
search_by_analogue(market_regime="credit-crunch", event_type="market-crash")

# Get full detail on a specific setup
get_technical_setup(setup_id="ts_pullback_to_20_bar_ema_in_strong_bull_trend")
```
