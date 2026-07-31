# Leading Indicators Framework — Detailed Methodology

Framework inspired by publicly taught professional trading frameworks; all text is an original paraphrase.

## Core Thesis

**Predict GDP → predict stock-market returns.** Historical evidence (281 quarters, 1950–2020): S&P 500 and US GDP move in the same direction 69.04% of quarters. Including profit-taking scenarios (S&P down / GDP up), 94.66% of quarters are explainable. The S&P 500 leads GDP by 6 months (max statistical significance: 10-year rolling correlation avg 0.56).

**Two analytical axes**:
- **Growth** drives E (earnings in the PE ratio)
- **Liquidity** drives P (price in the PE ratio)

---

## Step 1 — GDP Baseline & Correlation Check

**GDP Definition Hierarchy**:
- Nominal GDP: total income of a country in a given year.
- Real GDP: nominal GDP adjusted for inflation (CPI). Market commentators mean real GDP.
- Recession: two consecutive quarters of negative real GDP growth.

**Quadrinomial Method**: Compare quarterly S&P 500 returns (6-month lagged) against quarterly real GDP:
- 0-0: both down (8.19%) → sell / net short.
- 1-1: both up (60.85%) → buy / net long.
- 0-1: S&P down / GDP up (25.62%) → profit-taking; reduce risk.
- 1-0: S&P up / GDP down (5.34%) → unpredictable; maintain neutral.

**Statistical Correlation**: 10-year rolling correlation between S&P 500 (6-month lag) and real GDP YoY. 0.56 avg = moderate positive. Track if rising (growth-driven) or falling (liquidity/policy intervention-driven). Low correlation periods = high inflation / aggressive Fed intervention (mid-1980s, 2020).

**International Validation**: Apply quadrinomial + correlation to EuroStoxx 600 vs Eurozone GDP (72.28% same-direction). Shenzhen Composite vs Chinese GDP is unreliable (~0.05 correlation) — do not use as GDP proxy.

---

## Step 2 — Money Market Leading Indicators

Money markets provide the most reliable earliest signals. The Fed monitors these same indicators daily.

### 2a. Real Interest Rates (Leading Indicator #1)

Real rate = Nominal rate − CPI inflation. Nominal alone is meaningless. US 10-year Treasury is the risk-free benchmark — world's most liquid non-derivative debt; everything priced as a spread over it.

**DCF transmission**: Lower real rates → lower discount factor → higher PV of future cash flows → higher equity valuations. PE decomposition: Growth→E; Liquidity (via real rates)→P.

**Real rates vs S&P 500 PE**: Negative/near-zero real rates → PE expansion (S&P PE ~30 at zero-rate periods). Rising real rates → PE contraction. Lower real rates → less equity volatility (VIX compression). Higher real rates → more volatility.

**Classification**: Accommodative (< 0.5%), Neutral (0.5–2%), Restrictive (> 2%). Direction: falling = bullish equities; rising = bearish.

### 2b. Yield Curve (Leading Indicator #2)

2s10s spread is primary signal. Curve represents market expectation of short-term vs long-term economic risk:
- **Upward-sloping** (2s10s > 0): expansionary. Long bias.
- **Flattening** (2s10s → 0): transition. Reduce risk.
- **Inverted** (2s10s < 0): recession signal. Precedes recession by 6–18 months. Defensive/short bias.
- **Steepening from inversion**: recovery signal. Fed begins cutting. Long bias returns.

**TED spread** (3m LIBOR vs 3m Treasury): stress in Eurodollar / global USD funding. Widening = global dollar stress.

**International curves**: German Bunds, UK Gilts, JGBs. Same principles; use local CPI for real rates.

### 2c. Corporate Credit Spreads (Leading Indicator #3)

**Credit quality hierarchy** (ladder of risk sensitivity):
- **AA** (ICE BofA AA US Corporate Index, FRED): tightest spreads, systemic stress signal.
- **BBB** (ICE BofA BBB US Corporate Index, FRED): wider spreads. BBB-AA premium shows credit-quality rotation.
- **CCC / High Yield** (ICE BofA CCC US Corporate Index, FRED): widest, most volatile. Moves FIRST — "canary in coal mine."

**Decision rules**:
- Widening spreads = higher default risk → contractionary → sell. Economy follows 1–2 quarters later.
- Tightening spreads = lower default risk → expansionary → buy.
- CCC blowout 400+ bps while AA/BBB calm = stress concentrated in weakest firms. Monitor contagion.

**DCF linkage**: Wider spreads → higher debt cost → lower future cash flows → lower PV → lower equity. Compounding: expensive debt also reduces borrowing.

**Retail tradable proxies** (indicators, not standalone trades): LQD (IG ETF), HYG (high yield), JNK (junk).

### 2d. M2 Money Supply Growth (Accessory)

Role: confirms/contradicts real rates, curve, spreads. Not standalone. Expanding M2 + falling real rates = expansionary confirmed. Decelerating M2 + rising real rates = contractionary confirmed. Falling real rates + stagnant M2 = regime ambiguity — flag.

---

## Step 3 — Survey-Based Indicators

Surveys capture the two private-sector entities: businesses (ISM) and consumers (UMCSI).

### 3a. ISM Manufacturing PMI (Leading Indicator #4)

Monthly purchasing-manager survey. PMI > 50 = expansion, < 50 = contraction. Turns 3–6 months before broad economy. Most closely watched by pros and Fed.

**Key sub-components**: New Orders (most forward-looking, leads production by 1–3 months), Supplier Deliveries (slowing = inflationary), Employment. PMI trajectory > absolute level. PMI < 45 = strong contraction.

### 3b. Consumer Sentiment — UMCSI (Leading Indicator #5)

Consumer spending = ~70% of US GDP. Sentiment leads spending by 1–3 months. Below 70 = recession warning. Above 90 = confident. Sharp MoM drops > 5 points often precede equity corrections. Monitor gap between Current Conditions and Expectations indices.

---

## Step 4 — Cyclical Commodity Prices

Real-time physical demand signals.

**Copper ("Dr. Copper")**: Input to construction, manufacturing, electrical — pervasive. Rising = expansion; falling = slowdown. Compare LME (global) vs Shanghai (China). Divergence = regional decoupling.

**Brent Crude**: Rising + rising copper = demand-driven expansion (bullish). Rising + falling copper = supply shock or stagflation (bearish equities).

**Additional**: Iron ore (steel/construction), natural gas (industrial), lumber (housing).

---

## Step 5 — Stock Market & Forex

**S&P 500**: Ultimate leading indicator — trades daily, prices future GDP 6 months ahead. Falling S&P + positive GDP (25.62%) = typically profit-taking, not regime change. Sustained decline (> 2 quarters) + deteriorating leading indicators = genuine contraction.

**DXY**: Dollar is reserve currency. Strengthening = tightening global conditions. Weakening = loosening. DXY rising + widening credit spreads = double-confirmation tightening. DXY falling + tightening spreads = double-confirmation loosening. DXY rising + tightening spreads = conflict — flag.

---

## Step 6 — Coincident & Lagging Cross-Check

- **Coincident** (monthly): CPI, PPI, Employment Situation Report (NFP). Rising CPI + rising employment + falling leading indicators = late-cycle, potential stagflation.
- **Lagging** (quarterly): GDP is lagging (reported 1 month post-quarter). Corporate earnings, unemployment. Never trade off lagging alone; confirm/refute what leading indicators signaled.

---

## Step 7 — International Leading Indicators

**European ESI**: Composite business + consumer confidence. Functions like ISM+UMCSI for Europe.

**China PMI (Official vs Caixin)**: Official = SOE/large firms. Caixin = smaller private. Caixin often leads Official by 1–2 months. China real interest rates provide liquidity dimension.

**Other**: Japan Tankan + JGB curve; UK Gilt curve + UK PMI; Germany Bund curve + Ifo Business Climate; Italy BTP-Bund spread (sovereign credit proxy). Use local CPI for real rates.

**Eurodollar market**: USD held outside US banks (LIBOR/SOFR). TED spread blowout = global dollar funding stress → affects all equity markets.

---

## Step 8 — Dashboard & Bias Resolution

Weighted scorecard with 11 indicator categories:

| Indicator | Expansionary Signal | Contractionary Signal | Weight |
|-----------|--------------------|------------------------|--------|
| Real Rates | Negative / Falling | Positive / Rising | High |
| Yield Curve 2s10s | Steep / Steepening | Flat / Inverted | High |
| Credit Spreads | Tightening | Widening | High |
| M2 Money Supply | Accelerating | Decelerating | Medium |
| ISM PMI | > 50, Rising | < 50, Falling | High |
| UMCSI | > 90, Stable | < 70, Falling | Medium |
| Copper | Rising | Falling | Medium |
| Brent Crude | Rising w/ Copper | Rising w/o Copper | Low |
| S&P 500 | Rising | Sustained Decline | High (confirming) |
| DXY | Falling | Rising | Medium |
| International | Expansionary | Contractionary | Medium |

**Bias rule**: ≥ 60% expansionary → net long. ≥ 60% contractionary → net short. Mixed → neutral (hedged/pair-trade).

**Caveats**: Fed watches same indicators; may intervene (conventional rate changes or unconventional bond buying). Fed action can reverse/delay signals. No mechanical rules — context, magnitude, speed matter. Central bank actions can panic as much as placate if outside market expectations.

---

## Step 9 — Analogue Retrieval

Query `search_by_analogue` with: `market_regime` (expansion/contraction/stagflation/recovery), `event_type` (rate-hike-cycle/rate-cut-cycle/yield-curve-inversion/credit-crunch/commodity-shock). Surface parallels and differences. Cite via `/v/` links.

---

## Step 10 — Regime Classification

Four states with probability weights (Bear/Base/Bull) and transition catalysts:
1. **Expansion** — growth accelerating, liquidity abundant, spreads tightening, equities rising.
2. **Contraction / Recession** — growth decelerating, liquidity scarce, spreads widening, equities falling.
3. **Stagflation** — growth stagnating, inflation elevated, real rates negative, commodities rising, equities range-bound.
4. **Recovery** — emerging from contraction, leading indicators turning up, curve steepening from inversion.
