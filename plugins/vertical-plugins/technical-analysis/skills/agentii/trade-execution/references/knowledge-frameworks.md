# Trade Execution — Knowledge Base Integration

This skill handles entry execution, position sizing, stop placement, scaling, and exit management. The knowledge base provides specific operational parameters for each setup.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `search_technical_setups` | Find execution setups by pattern, timeframe, market condition |
| `get_technical_setup` | Full detail: entry_setup, confirmation_signals, exit_rules, invalidation, typical_rr_ratio, win_rate_context |
| `search_by_analogue` | Cross-reference with historical situations |

## Execution Parameters Available

Each of the 686 setups in `gold.technical_setups` provides:

| Field | Coverage | Description |
|-------|:---:|------|
| entry_setup | 100% | Specific entry trigger conditions |
| exit_rules | 100% | Stop placement, profit targets, time stops |
| invalidation | 100% | What invalidates the setup |
| edge_rationale | 100% | Why the setup has a statistical edge |
| typical_rr_ratio | — | Reward:risk profile |
| win_rate_context | — | Expected win rate with sample size |
| entry_predicates | — | Structured entry conditions (bar quality, pattern signature) |
| market_gates | — | Market condition filters for execution |

## Position Sizing Frameworks

Search for setups with specific risk profiles:
```
# Find setups with explicit R:R ratios
search_technical_setups(search="risk reward ratio")

# Find setups mentioning specific stop placement rules
search_technical_setups(search="stop below signal bar")

# Find scaling setups
search_technical_setups(search="scale out take profit")
```

## Exit Strategy Categories

| Exit Type | Setup Examples |
|-----------|---------------|
| Fixed stop | Stop below/above signal bar, swing low/high |
| Trailing stop | Trail on higher timeframe structure, 2-ATR trail |
| Time stop | Exit at market close, exit after N bars without progress |
| Profit target | Take half at 2R, runner; measured move target |
| Invalidation | Catalyst change, pattern failure, gap fill |

## Example Queries

```
# Find swing setups with favorable R:R
search_technical_setups(timeframe="swing", search="2:1 reward risk")

# Find intraday scalp setups
search_technical_setups(timeframe="intraday", market_condition="any")

# Get full execution detail
get_technical_setup(setup_id="ts_scaling_out_at_multiples_of_initial_risk")
```
