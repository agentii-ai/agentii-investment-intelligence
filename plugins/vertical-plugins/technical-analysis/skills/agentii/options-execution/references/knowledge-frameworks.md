# Options Execution — Knowledge Base Integration

This skill handles options strategy execution: strike selection, Greeks management, multi-leg structures, volatility trading. The knowledge base provides 82 options-specific setups with detailed parameters.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `search_technical_setups` | Find options setups by strategy type, instrument_scope |
| `get_technical_setup` | Full detail: option_legs, option_greeks, option_structure, option_scenarios, option_sensitivity |
| `search_by_analogue` | Find historical situations where options strategies were applied |

## Options Setup Categories (82 setups)

| Strategy Family | Setups | Key Parameters |
|----------------|:-----:|---------------|
| Covered Call | 12 | Strike selection (delta 0.25-0.30), DTE 30-45, roll management |
| Bull/Bear Spread | 15 | Debit/credit spread construction, strike width, risk/reward |
| Ladder Spread | 8 | Bull call ladder, bear put ladder, ratio configurations |
| Straddle/Strangle | 10 | ATM/OTM selection, IV percentile thresholds, earnings plays |
| Collar | 5 | Protective collar, zero-cost construction |
| Naked Put | 6 | Premium selling on quality stocks, elevated IV entry |
| Ratio Spread | 7 | 1x2, 1x3 ratio configurations, backspreads |
| Long Call/Put | 5 | Catalyst-driven, 1:3 risk/reward discipline |
| VIX Hedging | 4 | IV spike portfolio protection, exposure reduction |
| Strike Selection | 6 | ATM vs OTM criteria, liquidity filters |
| Greeks Management | 4 | Delta, gamma, theta, vega thresholds |

## Options-Specific Fields

Each options setup provides structured data:

| Field | Description |
|-------|-------------|
| `option_legs` | Multi-leg structure: long/short, strike, expiration, ratio |
| `option_greeks` | Delta, gamma, theta, vega targets and thresholds |
| `option_structure` | Strategy classification: directional, volatility, income |
| `option_scenarios` | Bull/bear/flat scenarios with P&L projections |
| `option_sensitivity` | IV expansion/contraction impact, time decay curves |

## Retrieval Strategy

1. **Classify strategy type** (directional, income, volatility, hedging)
2. **Search by instrument_scope** to filter options setups
3. **Filter by market_condition** — elevated IV favors premium selling, low IV favors directional
4. **Get full detail** for option_legs and option_greeks on top matches

## Example Queries

```
# Find covered call setups
search_technical_setups(search="covered call", instrument_scope="option")

# Find volatility expansion setups for earnings
search_technical_setups(pattern_type="volatility_expansion", market_condition="volatile")

# Get full options detail with Greeks
get_technical_setup(setup_id="ts_otm_covered_call_30_45_dte_strike_025_030_delta")
```
