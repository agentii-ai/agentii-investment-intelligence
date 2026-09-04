# TIER Equity Research Workflow — Institutional Consensus

Methodology from professional equity research training frameworks, now incorporated into CFA Institute Level II curriculum (2024). All text is an original paraphrase.

---

## The TIER Workflow

TIER is a structured 4-step equity research process designed to produce investment recommendations with explicit catalysts, price targets, and differentiation from consensus. It is the institutional standard for professional equity research workflow.

### T — Target Realistic Prices

**Objective**: Establish a well-supported price target range.

**Process**:
1. Build financial forecasts (income statement, balance sheet, cash flow)
2. Apply the appropriate valuation methodology using the structured selection framework
3. Derive a price target range (upper bound, lower bound, central estimate)
4. Document the key assumptions that drive the target

**Price Target Format**: Not a single number. A range reflecting the uncertainty in key assumptions. The width of the range communicates conviction.

### I — Identify & Forecast Catalysts

**Objective**: Determine what will cause the market to accept the investment thesis.

**Process**:
1. Identify all potential catalysts within the investment horizon
2. Classify: Scheduled (earnings, FDA dates) vs. Conditional (M&A, restructuring) vs. Macro-triggered
3. Assess each catalyst: specificity, magnitude, probability
4. Calendar the catalysts — what happens when
5. Determine: which catalyst is the primary one that will drive repricing?

**Key Question**: "What specific event will cause the market to agree with my thesis, and when will that happen?"

### E — Ensure Ideal Entry Point

**Objective**: Differentiate from consensus, check risks, and document the thesis.

**Process**:
1. **FaVeS Differentiation Check**: In what specific ways is this thesis different from consensus?
   - **F**orecast: Are my EPS/cash flow estimates different from consensus?
   - **V**aluation: Am I using a different valuation methodology or multiple?
   - **S**entiment: Is market sentiment mispricing this stock relative to fundamentals?
2. **Risk Check**: What would invalidate the thesis? Set explicit invalidation thresholds.
3. **Bias Check**: Am I anchoring on a prior view? Confirm the thesis is evidence-driven, not narrative-driven.
4. **Document the Thesis**: Write the thesis BEFORE entering the position. The documented thesis is the standard against which post-trade analysis is measured.

### R — Review Performance & Thesis

**Objective**: Maintain a dynamic assessment as new information arrives.

**Process**:
1. Maintain a dynamic comparable company table
2. After each catalyst event: did it resolve as expected? If yes, thesis intact. If no, reassess.
3. After each earnings report: track KPIs against thesis assumptions
4. Periodic review: even without a catalyst event, review thesis validity at regular intervals
5. **When to exit**: Catalyst resolved as expected (target approach) → take profits. Catalyst failed → exit immediately regardless of P&L. Thesis assumptions violated → exit. Better opportunity identified → rotate capital.

---

## SHARE Valuation Method Selection

SHARE is the embedded framework for selecting and applying the appropriate valuation methodology. It is not a valuation formula — it is a method-selection framework that ensures the valuation approach matches the business model.

### S — Select Optimal Valuation Method

The method must match the business model:

| Business Model | Primary Method | Rationale |
|---------------|:---:|------|
| Stable, mature, profitable | P/E (DCF cross-check) | Earnings are the primary value driver |
| Capital-intensive | EV/EBITDA, EV/EBIT | Capital structure and D&A distort P/E |
| High-growth, pre-profit | EV/Revenue, DCF | Earnings not yet meaningful |
| Financial services | P/B, P/TBV, Dividend Discount | Balance sheet is the business |
| Asset-heavy, cyclical | P/NAV, EV/EBITDA (normalized) | Cycle-average earnings |

### H — Historical & Current Data Review

- Review the company's own historical trading multiples (3-5 year range)
- Review sector median multiples and their historical range
- Review precedent transaction multiples (if relevant)
- Understand WHY the company trades where it does vs. its own history

### A — Adjust Multiples for Price Targets

- Adjust sector median multiples for company-specific factors: growth premium/discount, margin quality, ROIC differential, leverage, liquidity
- Derive justified forward multiples
- Apply to forward estimates (consensus or independent, depending on FaVeS differentiation)

### R — Range of Multiples & Price Targets

- Upper bound: Bull case estimates × upper-quartile or justified premium multiple
- Lower bound: Bear case estimates × lower-quartile or justified discount multiple
- Central: Base case estimates × justified multiple
- The range width signals conviction — narrow range = high conviction

### E — Evaluate as Circumstances Change

- Reassess multiples and targets after each catalyst event and earnings report
- Update the comparable company set as peers' businesses evolve
- The price target is a living estimate, not a static number

---

## ENTER Research Quality Gate

Before presenting any investment recommendation, apply the ENTER quality check:

- **E**vidence: Is every claim supported by specific, citable evidence?
- **N**umbers: Are all financial projections internally consistent? Cross-checked?
- **T**hesis: Is the variant view clearly articulated and differentiated from consensus?
- **E**xpectations: Is the expectations gap quantified (not just "the stock looks cheap")?
- **R**isk: Is the key risk identified and an invalidation threshold set?

---

## FaVeS Differentiation Check

The FaVeS framework ensures every thesis is explicitly differentiated from consensus. A thesis without differentiation is not a thesis — it is a description.

| Dimension | Consensus | My View | Evidence |
|-----------|-----------|---------|----------|
| **F**orecast | What EPS/revenue does consensus expect? | What do I expect? | KPI trends, management guidance analysis, industry data |
| **V**aluation | What multiple does the market apply? | What multiple is justified? | ROIC analysis, growth sustainability, peer comparison |
| **S**entiment | What is the market narrative? | Why is the narrative wrong? | Earnings call tone, analyst report language, positioning data |

A thesis is valid only when at least one of F, V, or S is DIFFERENT from consensus AND supported by specific evidence. A thesis where all three align with consensus is not an investment opportunity — it is a consensus description.

---

## Integration with Agentii Platform

TIER maps to the agentii skill ecosystem as follows:

- **T (Target)**: `valuation-methods` + `trade-template` (price target derivation with SHARE)
- **I (Identify Catalysts)**: `qualitative-filtering` (catalyst identification)
- **E (Ensure Entry)**: `qualitative-filtering` (FaVeS variant view) + `risk` (invalidation thresholds)
- **R (Review)**: `trading-as-business` (post-trade analysis)

TIER provides the **institutional consensus workflow** that orchestrates across these individual skills. It answers the question: "What is the professional process for converting raw analysis into an investment recommendation?"
