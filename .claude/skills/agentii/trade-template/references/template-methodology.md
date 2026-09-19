# Trade Template Methodology

Methodology fused from professional investment frameworks; all text is an original paraphrase.

---

## The Trade Template Purpose

A trade idea without a template is an opinion. With a template, it is a testable hypothesis. The template transforms qualitative thinking and quantitative analysis into a structured, comparable, and reviewable format. Every trade that succeeds or fails becomes a learning data point because the template captures what was known, believed, and assumed at the time of entry.

The core formula: **Trade Idea = Fundamentals + Timing + Trade Structure**. The template operationalizes this formula into concrete numbers, explicit price levels, and probability-weighted scenarios.

---

## Price Target Derivation: Three-Method Framework

Apply multiple independent valuation approaches. Agreement across methods increases confidence. Divergence requires investigation — it signals that one or more assumptions may be wrong.

### Method 1: P/E Multiple Approach

This is the primary method for companies with meaningful and relatively stable earnings.

**Step 1: Derive Justified Forward P/E**

The justified P/E is NOT simply "pick a number." It is triangulated from three independent sources:

1. **Historical Range**: The stock's own 3-5 year forward P/E range. Use the 25th to 75th percentile. Adjust for material business changes — if the company was a 5% grower historically and is now a 15% grower, the historical range understates the justified multiple.

2. **PEG-Implied P/E**: Justified P/E = Forward EPS Growth Rate × Sector-Justified PEG Ratio. The sector-justified PEG is the median PEG for the sector, adjusted for the company's growth quality premium or discount. Example: 20% forward growth × 1.2x sector PEG (vs. 1.0x median) = 24x justified P/E.

3. **Sector Median P/E with Growth Adjustment**: Start with the sector median forward P/E. Adjust upward if the company's growth rate exceeds the sector median, downward if below. Rule of thumb: each 5 percentage points of growth above sector median justifies roughly 10-15% multiple premium, though this varies by sector.

**Step 2: Apply to Forward EPS**

```
PT (P/E Upper) = Bull Case Forward EPS × Upper Quartile P/E (75th percentile)
PT (P/E Lower) = Bear Case Forward EPS × Lower Quartile P/E (25th percentile)
PT (P/E Central) = Base Case Forward EPS × Justified P/E (triangulated)
```

### Method 2: EV/EBITDA Approach

Preferred for: capital-intensive industries where depreciation distorts earnings, highly leveraged companies where capital structure differences make P/E comparisons misleading, and M&A contexts where enterprise value is the acquisition currency.

**Step 1: Derive Justified EV/EBITDA**

Start with the sector median forward EV/EBITDA. Adjust:
- Growth premium: above-sector growth → premium to median. Below-sector growth → discount.
- Margin quality: above-sector EBITDA margins → premium (higher quality earnings). Below-sector → discount.
- ROIC differential: above-sector ROIC → premium. Below-sector → discount.

**Step 2: Calculate Target Enterprise Value and Equity Value**

```
Target EV = Forward EBITDA × Justified EV/EBITDA
Target Equity Value = Target EV - Net Debt (Total Debt - Cash)
Target Price = Target Equity Value / Diluted Shares Outstanding
```

### Method 3: Sales Multiple Approach

For: pre-profit or early-stage companies where earnings are not meaningful, highly cyclical companies where earnings fluctuate wildly, and asset-light businesses where revenue scale is the primary value driver.

**Critical adjustment**: The P/S multiple MUST be contextualized by the margin profile. A 5% net margin company trading at 2x P/S is more expensive than a 20% net margin company trading at 4x P/S. The formula: P/S ÷ Net Margin = Implied P/E Equivalent.

```
PT (Sales) = (Forward Revenue × Justified P/S Multiple) / Diluted Shares Outstanding
```

Revenue quality adjustments:
- Recurring/subscription revenue: deserves premium (visibility)
- One-time/license revenue: deserves discount (lumpy, unpredictable)
- Revenue concentration (> 25% from single customer): deserves discount (key-man risk at the customer level)

### Blending the Methods

Weight each method by business model suitability. Agreement across methods increases target confidence; divergence signals that the business model doesn't fit neatly into standard frameworks — proceed with caution.

| Business Model | PE Weight | EV/EBITDA Weight | P/S Weight | P/B Weight |
|---------------|:---:|:---:|:---:|:---:|
| Asset-light growth (SaaS, platforms, services) | 60% | 30% | 10% | — |
| Capital-intensive (manufacturing, energy, industrials) | 30% | 50% | 20% | — |
| Financial services (banks, insurance) | 50% | — | — | 50% |
| Pre-profit / early-stage | — | 30% | 70% | — |
| Real estate / asset-heavy | — | 50% | 30% | 20% (P/NAV) |

**Upper and lower bounds**: The price target is not a single number but a range. Upper bound = bull case metrics × upper-quartile multiples. Lower bound = bear case metrics × lower-quartile multiples. The central target is the probability-weighted expected value.

---

## Trading Comps Spreading: Complete Workflow

Comparable company analysis is the market-based sanity check on intrinsic valuation. The institutional workflow:

### Step 1: Select the Peer Group
4-6 comparable companies selected via dual-path methodology (see quant-methodology.md). The peer group must be:
- Industry-comparable (similar business models, end markets, regulatory environments)
- Fundamentals-comparable (similar growth rates, margin profiles, ROIC levels)
- Size-comparable (market cap within 0.3x-3x of target, or closest available)

### Step 2: Spread Financial Data
For each peer and the target, compile:
- Revenue, EBITDA, EBIT, Net Income, EPS, FCF
- Last 3 fiscal years (historical) + current year estimate + next year estimate
- Source: SEC XBRL facts for historicals, consensus estimates for forward

### Step 3: Calculate Multiples
For each company, calculate:
- **LTM multiples**: based on last twelve months of reported data
- **Forward multiples**: based on current and next year estimates
- **Growth-adjusted multiples**: P/E ÷ Growth (PEG), EV/EBITDA ÷ Growth

### Step 4: Non-GAAP Normalization
Adjust peer multiples for accounting differences to ensure comparability:
- **SBC treatment**: If peers have materially different SBC policies, adjust to a consistent basis
- **Amortization policies**: Different useful-life assumptions for intangibles affect EBIT and EBITDA
- **Non-recurring items**: Strip out genuinely non-recurring items from all peers
- **Lease accounting**: Ensure operating vs. finance lease classification is consistent

### Step 5: Calendarization
Align fiscal years when peers have different year-ends. Calculate calendar-year estimates by weighting fiscal-year estimates based on month overlap. This is essential for sectors with different fiscal conventions.

### Step 6: Calculate Peer Group Statistics
For each multiple, calculate: median, mean, 25th percentile, 75th percentile. Use median (not mean) as the primary central tendency measure — the mean is skewed by outliers.

### Step 7: Apply to Target
Target multiple = peer group median ± adjustment for differences in:
- Growth rate (higher → premium)
- Margin profile (higher → premium)
- ROIC (higher → premium)
- Leverage (higher → discount, all else equal)
- Liquidity / size (smaller → discount)

### Step 8: Build the Football Field
Synthesize all valuation approaches into a single visual range comparison:
- Trading comps range
- DCF valuation range (if available)
- Transaction comps / precedent transactions range (if available)
- 52-week trading range
- Current price marker

The football field shows where the current price sits relative to multiple independent valuation methodologies. A price near the bottom of multiple ranges with fundamental support is a stronger signal than a price near the top.

---

## Shares Outstanding: Dilution Calculation

For accurate per-share metrics, diluted shares outstanding must include all sources of potential dilution:

### Treasury Stock Method (Options and Warrants)
Only in-the-money options and warrants are dilutive. The formula assumes:
1. Option holders exercise at the strike price → company receives cash proceeds
2. Company uses proceeds to repurchase shares at the average market price
3. Net new shares = Options Exercised - Shares Repurchased

### If-Converted Method (Convertible Debt and Preferred Stock)
Assumes conversion at the beginning of the period (or issuance date if later). For convertible debt: add back after-tax interest expense (since it would not have been paid if converted), then divide adjusted net income by the increased share count.

### Restricted Stock and RSUs
Included in basic shares upon vesting. Unvested RSUs are included in diluted shares using the treasury stock method (with a zero strike price, since the employee pays nothing upon vesting).

### Dual-Class Shares
Use shares of the class being traded. If the classes have different economic rights, adjust accordingly. If the company has a dual-class structure with super-voting shares, note the governance implications but calculate per-share metrics based on total economic shares.

---

## GAAP / Non-GAAP Reconciliation

### The SBC Debate

Share-based compensation is the single most contentious non-GAAP adjustment. Two perspectives, both valid in different contexts:

**The Economic Cost View**: SBC is ALWAYS a real cost. It transfers value from existing shareholders to employees through dilution. Excluding SBC from earnings systematically overstates the earnings available to shareholders. This view is correct for intrinsic valuation — the true economic earnings of the business are GAAP earnings including SBC.

**The Comparability View**: SBC may be excluded for comps purposes IF peers have materially different SBC practices. A company paying employees entirely in cash vs. a competitor paying heavily in stock will show very different GAAP earnings even if total compensation costs are identical. Adjusting SBC enables apples-to-apples comparison of operating performance.

**Institutional practice**: Include SBC for intrinsic valuation. May exclude for comps comparability but MUST flag the adjustment and quantify the impact. The SBC red line: SBC > 10% of revenue indicates structural earnings quality issues requiring investigation.

### Non-Recurring Items: The Complete Checklist

Items to identify and assess in the GAAP/non-GAAP reconciliation:

- Restructuring charges and severance costs
- Asset impairments and write-downs
- Litigation settlements and legal reserves
- M&A transaction and integration costs
- Gains or losses on asset sales
- Debt extinguishment (early repayment penalties, write-off of unamortized issuance costs)
- Tax settlements and valuation allowance changes
- Inventory write-downs
- Goodwill impairment
- Insurance recoveries
- Currency translation gains/losses (if not operational)

### The "Too Many Non-Recurrings" Rule

If charges described as "non-recurring" or "one-time" appear in 3 or more of the last 4 quarters, they are recurring by definition. Management is using non-GAAP adjustments to mask structural cost issues. Reclassify these items as recurring operating expenses before proceeding with any valuation.

### Normalized Earnings Calculation

```
Normalized Net Income = GAAP Net Income
  + Non-recurring charges (if truly non-recurring)
  - Non-recurring gains (if truly non-recurring)
  + SBC add-back (for comps comparability only — flag that this was done)
  = Normalized Earnings
```

The normalized earnings figure is used for P/E-based valuation. The unadjusted GAAP figure is always shown alongside for transparency.

---

## Scenario Construction

Every trade template must include three probability-weighted scenarios. The scenarios are not academic exercises — they define the risk/reward parameters that determine position sizing and entry decisions.

### Probability Calibration

```
Base Case: 55% probability
  - Most likely outcome given current information
  - Consensus estimates as starting point, adjusted by analyst's variant view
  - Justified multiple applied to base case EPS
  - This is the "thesis plays out as expected" scenario

Bull Case: 20% probability
  - All catalysts materialize positively and on schedule
  - Multiple expansion beyond justified level (sentiment tailwind)
  - Margin improvement beyond base case assumptions
  - Revenue acceleration from positive macro or competitive developments

Bear Case: 25% probability
  - Primary catalyst fails or is significantly delayed
  - Multiple contraction (sentiment headwind)
  - Competitive pressure or macro headwind intensifies
  - Margin compression from cost inflation or pricing pressure
```

### Expected Value and Margin of Safety

```
Probability-Weighted Expected Value = Σ(Scenario Value × Probability)

Margin of Safety = (Expected Value / Current Price) - 1

Position Sizing Decision:
  MoS > 30%: High conviction → standard position size (5%)
  MoS 15-30%: Medium conviction → half position size (3%)
  MoS < 15%: Low conviction → watchlist, do not enter
  MoS negative: Thesis is broken → discard
```

The bear case must be genuinely adverse — not a "slightly worse base case." The test: would this scenario make you want to exit the position? If the answer is no, the bear case is not bearish enough.

---

## Thesis Writing: The One-Paragraph Format

The investment thesis is the single most important output of the template. It must be concise, falsifiable, and contain five required elements.

### The Format
```
"The market believes [consensus view — what is currently priced into the stock]. 
We believe [variant view — what is different from consensus and why] 
because [1-2 specific, verifiable pieces of evidence]. 
This divergence will converge when [specific, dateable catalyst] occurs 
within [timeframe], generating approximately [expected return] 
against a primary risk of [key downside scenario]."
```

### The Five Required Elements

1. **Consensus View**: What does the market currently believe about this company? If you cannot articulate consensus, you cannot have a variant view. The consensus is typically embedded in the current stock price and sell-side analyst estimates.

2. **Variant View**: What do you believe that is DIFFERENT from consensus? "The company is growing revenue at 15%" is not a variant view if consensus also expects 15% growth. "The market is pricing 10% terminal growth but we believe structural demand supports 15%" — that is a variant view.

3. **Catalyst**: What specific, dateable event will cause the market to recognize the variant view? "Eventually the market will figure it out" is not a catalyst. "The Q3 earnings report will show revenue acceleration from 8% to 14% driven by the new product cycle" — that is a catalyst.

4. **Expected Return**: Quantified and probability-adjusted. "The stock could go up" is not a return estimate. "$150 price target vs. $100 current price = 50% upside, probability-weighted to 27.5% expected return" — that is a return estimate.

5. **Key Risk**: What could go wrong? What would invalidate the thesis entirely? If the analyst cannot identify a credible risk, the analysis is incomplete. Every thesis has a counter-thesis.

### Common Thesis Failures
- **The Company Description**: "Company X is a leading provider of..." This describes the company. It does not state a thesis.
- **No Variant View**: "The company is growing and the stock is cheap." Relative to what? Different from what consensus?
- **No Catalyst**: "Over time, the market will recognize the value." Not actionable for a 20-60 day trader.
- **Too Long**: If the thesis cannot fit in one paragraph, the analyst has not identified the 3-5 factors that truly matter. The details go in the template sections; the thesis is the synthesis.
- **No Risk Acknowledged**: Sign of overconfidence or incomplete analysis. Every thesis has a vulnerability.

---

## The 20-60 Day Horizon Flexibility Rule

The 20-60 day window is a guide, not an exact science. Trades sometimes hit price targets within 20 days on a probabilistic scenario and are closed early. Other times, the catalyst is slightly delayed and the position drifts past 60 days.

The "gray area" between 60 and 120 days requires particular intellectual honesty. Every day that passes without the catalyst materializing, the thesis is transitioning from trade to investment. The analyst must set a hard review date at Day 60: either the catalyst is in sight and the position is justified, or the thesis is drifting and the position should be closed regardless of current P&L.

The test: if you would not initiate the position today at the current price with the current catalyst timeline, you should not continue holding it either. Every day is a decision to stay in the trade.

---

## Position Sizing Framework

### Base Sizing
Default single position: 3-5% of portfolio gross exposure. With 10-15 positions in active inventory, this allocates 30-75% of capital to active trades with the remainder in cash or hedges.

### Sizing Adjustments

**Conviction Adjustment**:
- High conviction (multiple confirming signals, clear catalyst): upper range (5%)
- Medium conviction (some confirming signals, moderate catalyst clarity): mid-range (3-4%)
- Low conviction (single signal, uncertain catalyst): lower range (2-3%) or watchlist

**Catalyst Type Adjustment**:
- Binary catalyst (FDA decision, deal close): reduce position size by 25-33%. The discontinuous outcome distribution means the position could gap from profit to loss overnight.
- Spectrum catalyst (earnings report, sector re-rating): standard sizing. The continuous outcome distribution allows for managed exits.

**Risk/Reward Adjustment**:
- R/R > 3:1: upper range — the payout justifies full sizing
- R/R 2:1 to 3:1: standard range — acceptable for a diversified portfolio
- R/R < 2:1: lower range or skip — the edge may be too small to justify the risk

**Correlation Check**:
- Is this idea highly correlated with existing positions? If adding to an already-represented sector or factor, reduce size or replace the duplicative existing position.
- Total exposure to any single sector should not exceed 25% of portfolio. Total macro-driven exposure should not exceed 40%.

---

## MCP Integration

```
search_investment_strategies(domain=fundamental, kind=thesis)
  → validate thesis structure against known strategy frameworks
  → find templates for similar investment theses

search_investment_cases(domain=fundamental, sectors_focus=[derived])
  → find historical cases with similar thesis structures
  → assess how comparable theses resolved and over what timeframe

search_investment_strategies(domain=fundamental, sectors_focus=[derived])
  → sector-specific valuation multiples and benchmarks
  → common thesis patterns for the sector
```

---

## Output: The Football Field Matrix

The football field is the visual synthesis of all valuation work. It displays:

- **Trading Comps Range**: 25th to 75th percentile of peer-implied valuation
- **DCF Range**: Bull to Bear case from discounted cash flow (if available)
- **Transaction Comps Range**: Precedent transaction implied valuations (if available)
- **52-Week Trading Range**: The stock's own historical price range
- **Current Price**: Where the stock trades today
- **Target Price Range**: The analyst's derived range from the three methods above

A price near the bottom of multiple independent valuation ranges, with a catalyst for convergence, is the strongest possible setup. A price near the top of all ranges with deteriorating fundamentals is the clearest short signal.
