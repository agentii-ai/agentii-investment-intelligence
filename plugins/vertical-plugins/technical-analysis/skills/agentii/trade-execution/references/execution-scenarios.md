# Trade Execution — Advanced Methodology

Methodology inspired by price action trading methodology; all text is an original paraphrase.

---

## Trading MTR Tops

A Major Trend Reversal top is confirmed when the 5-step reversal sequence is complete. Trading it:

1. **Confirmation**: All 5 steps completed — pullback broke trend line, tested MA, trend resumed, second pullback at old extreme, grew into reversal.
2. **Entry**: Sell below the low of the signal bar that confirms the reversal (usually a strong bear bar closing on its low after the failed second push).
3. **Stop**: 1 tick above the most recent swing high (the failed second push high).
4. **Target**: Minimum 2x risk (swing). Measured move = height of prior bull trend projected downward from reversal point.
5. **Invalidation**: Price closes above the failed second push high before the trade triggers.

---

## Trading MTR Bottoms

Mirror of MTR tops, for bullish reversals:

1. **Confirmation**: All 5 steps completed in a bear trend.
2. **Entry**: Buy above the high of the signal bar confirming the reversal.
3. **Stop**: 1 tick below the most recent swing low.
4. **Target**: Minimum 2x risk (swing). Measured move upward.
5. **Invalidation**: Price closes below the swing low.

---

## Trading MTR Failures — **The Strongest Continuation Signal**

This is the most powerful setup in the  system. When the market begins a reversal sequence (Steps 1-3 occur) but the reversal FAILS (price breaks back through the trend line in the original direction):

1. **What happens**: The market breaks the trend line (Step 1), tests the MA (Step 2), resumes the trend (Step 3), but then instead of forming a second pullback (Step 4), the trend breaks out with renewed force.
2. **Why it's so powerful**: Everyone who entered the reversal gets trapped. Their stops become fuel for the continuation move.
3. **Entry**: Enter immediately when price breaks back through the trend line in the original trend direction with a strong bar.
4. **Stop**: 1 tick beyond the extreme of the failed reversal attempt.
5. **Target**: The original trend resumes — often accelerates. Swing at least part of the position.

**Key rule**: MTR failure = the strongest form of trend continuation. It is higher probability than a new MTR trade.

---

## Trading a Strong Bull Breakout

### Recognition
- Big bull trend bars appearing
- Consecutive strong bull bars (2-4 bars)
- Small tails on these bars
- Context: breakout from trading range or channel

### Entry Methods (aggressive — strong means enter NOW)
1. Buy at the market — do not wait for pullback
2. Buy at close of any strong bull (or even bear) trend bar
3. Buy above the prior bar (stop entry)
4. Buy below the prior bar (if bull pressure is extreme, bears can't push down)
5. Press bets — buy breakouts above prior swing highs (scale in)
6. Buy small pullbacks (1-2 bar pullbacks)

### Stop Management
- Initial stop: below the most recent swing low or 1 tick below breakout point
- In a strong breakout, the stop can be wider (strong breakouts don't pull back much)

### Profit Management
- Try to **swing** at least part of the position (let profits run)
- For the scalp portion: use tighter stop, reward as big as risk (1:1)

### Distinguishing Strong vs Weak Breakouts
- **Strong**: Multiple consecutive big bars, small tails, follow-through → swing
- **Weak**: Single breakout bar, large tail, immediate deep pullback → scalp only

---

## Trading a Strong Bear Breakout

Mirror of the strong bull breakout for bear breakouts. Same principles inverted:
- Sell market, sell close of any strong bear bar, sell below prior bar
- Press bets on new swing lows
- Stop above most recent swing high
- Swing part, scalp part

---

## Trading a Strong Bull Channel

A strong bull channel has persistent upward movement with visible pullbacks contained by the trend line:

1. **Strategy**: Buy pullbacks to the trend line. Do NOT short the channel top.
2. **Entry**: Near the lower channel line (trend line), on an H2 or H3 pullback.
3. **Stop**: 1 tick below the signal bar low.
4. **Target**: Channel top (channel line). Minimum 2x risk.

### Why not fade a strong channel?
In a strong bull channel, shorts at the top have poor risk/reward. The channel weakens slowly over many bars. Shorts get crushed in the final spike before the channel actually breaks. Wait for the channel to clearly break before shorting.

---

## Trading a Strong Bear Channel

Same as the strong bear channel but inverted:
- Sell rallies to the upper channel line
- Do NOT buy the channel bottom
- Target: channel bottom

---

## Trading a Weak Bull Channel

A weak bull channel has broader bars, more overlap, and frequent tests of both boundaries:

1. **Strategy**: Fade the channel — sell near the top. Buy pullbacks is lower probability.
2. **Entry**: Near the upper channel line, when price shows a reversal bar.
3. **Stop**: 1 tick above the reversal bar high.
4. **Target**: Channel bottom (trend line).

**Why different from strong channel?** In a weak channel, the upward momentum is unreliable. Price frequently tests both boundaries. Selling the top captures the predictable return to the channel bottom.

---

## Trading a Weak Bear Channel

Same as the weak bear channel but inverted:
- Buy near the lower channel line (fade the channel)
- Target: channel top

---

## Trading Channel Reversals

When a channel breaks and transitions into a new trend:

1. **Bull channel breaking down**: Price breaks below the bull trend line → bear channel or bear trend begins.
2. **Entry**: Sell first pullback to the broken trend line (now resistance).
3. **Bear channel breaking up**: Price breaks above the bear trend line → bull channel or bull trend begins.
4. **Entry**: Buy first pullback to the broken trend line (now support).

---

## Trading in Trading Ranges

1. **Boundary trades only**: Buy near low, sell near high. The middle of the range is unpredictable.
2. **Scalp**: Take profits quickly. TR trades have smaller targets than trend trades.
3. **Range breakout**: When price breaks out, follow it. The first breakout from a TR is often a strong trend.
4. **False breakouts**: If price breaks out but immediately reverses back into the range, it's a false breakout. Trade back toward the opposite boundary.
5. **TR compression**: As a TR narrows, it becomes a "coil." The eventual breakout will be explosive.

---

## Trading Opening Range Swings

The opening range (first 60 minutes of the trading day) sets the initial framework:

1. **Mark the opening range**: High and low of the first hour.
2. **Breakout trade**: If price breaks above the opening range high with strong bars → buy. Break below opening range low → sell.
3. **Reversal at boundaries**: If price tests a boundary and reverses with a strong counter-bar → fade the breakout.
4. **Opening range as support/resistance**: Once broken, the opening range boundaries become support (if broken above) or resistance (if broken below) for the rest of the day.
5. **Midday**: Trading swings based on the day's established range. Less aggressive.

---

## Execution Integration with gold.technical_setups

When the `trade-execution` skill identifies the market condition and desired pattern, it calls:

```
search_technical_setups(
  pattern_type=<derived from pattern>,
  market_condition=<current>,
  timeframe=<timeframe>,
  instrument_scope=[<equity|option|futures>]
)
```

The returned setup provides:
- `entry_setup`: Exact entry method
- `confirmation_signals`: What must be true before entering
- `exit_rules`: Stop placement and profit targets
- `invalidation`: Conditions that void the setup

The skill merges methodology rules with the matched setup's specific parameters to produce the final trade plan.

---

## Quick Reference: Setup → Strategy Matrix

| Setup Type | Market Condition | Entry | Stop | Target | Swing/Scalp |
|-----------|-----------------|-------|------|--------|:---:|
| MTR Top | Reversal from bull | Below signal bar low | Above swing high | 2x risk + measured move | Swing |
| MTR Bottom | Reversal from bear | Above signal bar high | Below swing low | 2x risk + measured move | Swing |
| MTR Failure | Failed reversal | Market in original direction | Beyond failed reversal extreme | Trend continuation | Swing |
| Strong Bull Breakout | Breakout up | Market / close of bar / above prior bar | Below breakout point | Swing target | Swing+Scalp |
| Strong Bear Breakout | Breakout down | Market / close of bar / below prior bar | Above breakout point | Swing target | Swing+Scalp |
| Strong Bull Channel | Trending up (channel) | H2 near trend line | Below signal bar | Channel top | Swing |
| Strong Bear Channel | Trending down (channel) | L2 near trend line | Above signal bar | Channel bottom | Swing |
| Weak Bull Channel | Trending up (weak) | Sell near channel top | Above reversal bar | Channel bottom | Scalp |
| Weak Bear Channel | Trending down (weak) | Buy near channel bottom | Below reversal bar | Channel top | Scalp |
| Channel Reversal | Channel break | First pullback to broken line | Beyond broken line | Next boundary | Swing |
| Trading Range | Ranging | Buy low / Sell high | Beyond boundary | Opposite boundary | Scalp |
| Opening Range | Day session | Breakout above/below OR fade reversal | Beyond boundary | Measured move | Depends |
