# Options Execution Strategies — Advanced Methodology

Methodology fused from professional options trading frameworks; all text is an original paraphrase.

---

## Options Execution Framework

Options in a technical trading context serve as execution tools — they are not independent strategies but instruments for expressing a directional or volatility view with defined risk parameters. The framework distinguishes between the retail approach (buying options for leverage) and the institutional approach (using options to improve entry price, reduce cost basis, and expand risk boundaries).

### Core Filters

Before selecting any options strategy, apply three filters:

1. **Liquidity Filter**: Bid-ask spread must be ≤5% of the option price. Wide spreads destroy edge. Trade only liquid strikes on liquid underlyings.
2. **Cost Filter**: Premium paid as percentage of position size must be justified by the thesis. Avoid overpaying for optionality.
3. **Volatility Filter**: Implied volatility (IV) rank or percentile. IV > 70th percentile = options expensive, favor selling strategies. IV < 30th percentile = options cheap, favor buying strategies.

---

## Strategy Matrix: Market Condition → Option Strategy

| Market View | Volatility Environment | Strategy | Risk Profile |
|-------------|----------------------|----------|-------------|
| Bullish, moderate conviction | Any | Long Call | Limited risk (premium paid), unlimited upside |
| Bullish, income focus | Any | Short Naked Put | Receive premium, obligation to buy if assigned |
| Neutral to slightly bullish | Low IV | Covered Call | Own underlying, sell call for income, capped upside |
| Bullish, capped upside | Moderate IV | Bull Call Spread | Buy lower strike call, sell higher strike call |
| Bearish, capped downside | Moderate IV | Bear Put Spread | Buy higher strike put, sell lower strike put |
| Bearish, aggressive | Any | Long Put | Limited risk, large profit on sharp decline |
| Neutral, high IV expected | High IV | Covered Call Collar | Covered Call + Protective Put |
| Expecting large move, direction unclear | Low IV | Long Straddle | Buy at-the-money call + put same strike and expiry |
| Expecting large move, wider range expected | Very low IV | Long Strangle | Buy out-of-the-money call + put different strikes |
| Bullish bias, large move expected | Low IV | Strap Straddle | Buy 2 calls + 1 put at same strike |
| Bearish bias, large move expected | Low IV | Strip Straddle | Buy 1 call + 2 puts at same strike |
| Bullish, prefer defined risk, lower cost | Moderate | Bull Ratio Spread | Buy 1 lower call, sell 2 higher calls |
| Bearish, prefer defined risk, lower cost | Moderate | Bear Ratio Spread | Buy 1 higher put, sell 2 lower puts |

---

## Strategy Details

### Long Call
- **Purpose**: Directional bullish exposure with defined risk.
- **Entry**: Buy call at strike slightly out-of-the-money (delta 0.40-0.60).
- **Expiry**: Minimum 45-60 days to expiration to allow time for thesis to play out.
- **Max risk**: Premium paid.
- **Max reward**: Unlimited (stock price − strike − premium).
- **Invalidation**: Thesis invalidated before expiry; time decay accelerates after 30 DTE.

### Short Naked Put
- **Purpose**: Generate income or acquire stock at a discount.
- **Entry**: Sell put at strike you would be willing to own the stock.
- **Expiry**: 30-45 days for optimal theta decay.
- **Max risk**: Strike price × 100 (if assigned); stock can go to zero.
- **Invalidation**: Stock breaks below strike significantly; fundamentals deteriorate.

### Covered Call
- **Purpose**: Income enhancement on existing long stock position.
- **Entry**: Sell call at strike above current price (out-of-the-money), typically delta 0.25-0.35.
- **Expiry**: 30-45 days. Roll before expiry if you want to maintain position.
- **Max risk**: Stock position decline minus premium received.
- **Invalidation**: Stock surges past strike — shares called away, upside capped.

### Bull Call Spread
- **Purpose**: Defined-risk bullish trade with lower cost than outright call.
- **Entry**: Buy lower strike call, sell higher strike call (same expiry).
- **Max risk**: Net debit (long call premium − short call premium).
- **Max reward**: Strike difference − net debit.
- **Best for**: Moderate bullish conviction with limited upside target.

### Bear Put Spread
- **Purpose**: Defined-risk bearish trade with lower cost than outright put.
- **Entry**: Buy higher strike put, sell lower strike put (same expiry).
- **Max risk**: Net debit paid.
- **Max reward**: Strike difference − net debit.

### Long Straddle
- **Purpose**: Profit from large price movement in either direction.
- **Entry**: Buy at-the-money call + at-the-money put (same strike, same expiry).
- **Max risk**: Total premium paid (both options).
- **Break-even**: Strike ± total premium.
- **Best for**: Pre-earnings, pre-FDA decision, pre-macro event — when large move expected but direction uncertain.
- **Caution**: Premium is high because you buy two options. Need a very large move to profit.

### Long Strangle
- **Purpose**: Similar to straddle but lower cost, wider break-even.
- **Entry**: Buy out-of-the-money call + out-of-the-money put (different strikes, same expiry).
- **Max risk**: Total premium paid (lower than straddle).
- **Break-even**: Lower strike − premium, Upper strike + premium.
- **Best for**: Expecting explosive move; willing to trade lower probability for lower cost.

---

## Execution Integration with gold.technical_setups

When executing options trades, query the setup database:

```
search_technical_setups(
  pattern_type=<options specific>,
  instrument_scope=["option"],
  market_condition=<current derived from price-action>,
  timeframe=<derived>
)
```

The pipeline contains ~82 option-specific setups including:
- Risk/reward discipline for long call options
- Covered call strategy variants (dividend stocks, losing positions, concentrated portfolios)
- Spread strategies (bull call, bear put, ratio spreads, ladder spreads)
- Capital constraint filters for options strategies
- Catalyst-driven options trading frameworks

---

## Key Execution Rules

1. **Never trade options without a directional or volatility thesis.** Options amplify — they do not create edge.
2. **Selling premium (theta) is a business, not a trade.** Consistency matters more than any single trade outcome.
3. **For buying strategies, time is the enemy.** Enter with sufficient time (45+ DTE). Exit or roll before 21 DTE.
4. **For selling strategies, time is the ally.** Enter at 30-45 DTE. Capture theta decay.
5. **Position sizing for options**: Risk no more than 2% of capital on any single options trade. For premium-selling strategies, size based on notional exposure, not premium received.
