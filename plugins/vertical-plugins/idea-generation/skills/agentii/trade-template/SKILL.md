---
name: trade-template
description: Standardized trade idea template, multi-method price target derivation PE and sales multiple approaches, GAAP to non-GAAP reconciliation, base bull bear scenario construction, investment thesis structuring, Zendesk-style case methodology
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Price targets project 12-month forward; 4 quarters default."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
retrieval_scope: structured_only
layer_tags: ["L2", "L3"]
min_tool_diversity: 2
parameter_free: false
---

> Methodology fused from professional trading and investment frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| target_horizon_months | 12 | Standard forward price target horizon |
| scenario_probability_sum | 100% | Bear + Base + Bull must sum to 100% |
| default_position_size | 3-5% | Standard single-position risk allocation |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Upstream outputs — quantitative screening results + qualitative filtering assessment
2. Market data — current price, sector multiples, historical ranges via market data tools
3. Strategy frameworks — `search_investment_strategies(kind=thesis)` for thesis construction methodology

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (d) Simple Lookup from `contracts/retrieval.md`: template methodology is embedded in this Protocol. Market data from data tools. Strategy frameworks via `search_investment_strategies` for thesis construction validation.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill converts quantitative and qualitative analysis outputs into a structured, actionable trade template. A trade idea without a template is an opinion; with a template, it is a testable hypothesis. Every trade outcome becomes a learning data point because the template captures what was known and assumed at entry.

Detailed methodology: price target derivation with formulas, comps spreading workflow, GAAP/non-GAAP rules, scenario construction with probability calibration, and position sizing framework are in `references/template-methodology.md`.

#### Steps

1. **Data Assembly**: Gather all upstream outputs (quant metrics, financial validation, qual assessments, management/board flags, peer group, macro bias). Organize into template sections. Flag gaps — incomplete templates cannot support capital allocation.

2. **Price Target Derivation** (three methods, blend by business model per reference weights table):
   - **P/E**: Justified P/E triangulated from: historical range 25th-75th percentile, PEG-implied (growth × sector PEG), sector median with growth adjustment. Upper/lower bounds from bull/bear EPS × quartile multiples.
   - **EV/EBITDA**: For capital-intensive, highly levered, M&A contexts. Sector median ± growth/margin/ROIC adjustment. Target equity = Target EV − Net Debt.
   - **Sales Multiple**: For pre-profit/cyclical. Adjust for margin profile (5% margin at 2x P/S > 20% margin at 4x P/S). Recurring revenue premium.
   - Blend: asset-light 60/30/10 (PE/EV-EBITDA/PS), capital-intensive 30/50/20, financials 50/—/50(P/B), pre-profit —/30/70.

3. **Trading Comps Spreading**: Select 4-6 peers via dual-path. Spread revenue, EBITDA, EBIT, EPS, FCF (3yr historical + 2yr forward). Normalize for SBC/amortization/non-recurring differences. Calendarize different fiscal years. Output median + quartiles. Target multiple = peer median ± adjustment for growth, margin, ROIC, leverage, liquidity.

4. **GAAP/non-GAAP Reconciliation**: Identify all differences (SBC, amortization, restructuring, impairments, litigation, M&A, asset sales, debt extinguishment, tax). SBC: always include for true economic cost; may exclude for comps ONLY with flag. SBC > 10% revenue = structural issue. "Non-recurring" in 3+/4 quarters = recurring. Normalized = GAAP NI + justified adjustments. Show GAAP alongside.

5. **Scenario Construction**: Base 55% (consensus + variant view), Bull 20% (all catalysts, multiple expansion), Bear 25% (catalyst failure, contraction). Probabilities sum to 100%. Bear must be genuinely adverse. EV = Σ(Value × Prob). Margin of Safety = (EV/Price)-1. > 30% high conviction, 15-30% medium, < 15% watchlist.

6. **Thesis Statement**: One paragraph, five elements: (1) consensus view, (2) variant view + why, (3) dateable catalyst, (4) quantified return, (5) key risk. Format: "Market believes [X]. We believe [Y] because [evidence]. Converges when [catalyst] within [timeframe], generating [return] against risk of [downside]." Avoid: describing company (no variant), no catalyst, too long, no risk.

7. **Position Sizing**: Default 3-5%. Conviction: high→5%, medium→3-4%, low→watchlist. Binary catalyst→reduce 25-33%. R/R > 3:1→upper, 2:1-3:1→standard, < 2:1→skip. Correlation check: correlated with existing→reduce/replace. Hard Day-60 review: no catalyst→exit. Build football field. Handoff complete template.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_trade-template_{affix}.md`

## Output Structure

1. **Executive Summary** — Thesis in one paragraph, price target, expected return, conviction level
2. **Company Overview** — Business description, sector, market cap, key financial summary
3. **Quantitative Summary** — Key screening metrics, outlier classification, financial validation highlights, peer group
4. **Qualitative Summary** — KPI assessment, MOP credibility (5-dimension scorecard), management/board quality flags, key catalyst(s)
5. **Price Target Derivation** — PE method (justified P/E triangulation), EV/EBITDA method, Sales Multiple method, blended target with weights, cross-checks
6. **Trading Comps Output** — Peer group with multiples, median/quartile statistics, calendarization notes, target multiple derivation
7. **GAAP/non-GAAP Reconciliation** — Key adjustments with justification, SBC assessment, normalized earnings calculation
8. **Scenario Analysis** — Bear (25%)/Base (55%)/Bull (20%) with probabilities, values, implied returns, probability-weighted expected value
9. **Investment Thesis** — Market view vs. variant view (all 5 required elements), catalyst for convergence, timeframe
10. **Risk Assessment** — Key risks, maximum adverse scenario, thesis invalidation triggers
11. **Position Recommendation** — Suggested position size with conviction/catalyst/RR rationale, entry strategy
12. **Football Field Matrix** — Trading comps vs. DCF vs. transaction comps vs. 52-week range vs. current price vs. target range
13. **Coverage Gaps** — Data limitations, assumptions flagged for monitoring

## Error Handling

| Error | Fallback |
|-------|----------|
| Insufficient data for price target | Use single-method approach; flag low confidence |
| GAAP/non-GAAP data unavailable | Use reported GAAP; flag potential distortion |
| No comparable peer group | Use historical company multiples; flag peer gap |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/template-methodology.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`