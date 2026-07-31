---
name: quantitative-screening
description: Quantitative stock screening, forward-looking valuation outlier detection, backward-looking financial statement validation, PEG ratio analysis, earnings growth profile assessment, turnaround vs value trap discrimination, data mining bias prevention
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "Multi-year financial data required for trend analysis; 8 quarters default."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
  - search_investment_cases
retrieval_scope: structured_only
layer_tags: ["L2"]
min_tool_diversity: 2
parameter_free: false
---

> Methodology fused from professional trading and investment frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| screening_universe | S&P 500 + Russell 1000 liquid | Broad enough for diversity, liquid enough for execution |
| historical_years | 5 | Minimum years of financial data for trend analysis |
| peg_threshold | 1.0 | PEG < 1.0 suggests undervaluation relative to growth |
| fcf_conversion_min | 70% | FCF/Net Income below 70% flags earnings quality issues |
| earnings_beat_threshold | 70% | Beat frequency above 70% suggests conservative guidance |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Quantitative methodology — `references/quant-methodology.md` (bundled screening framework)
2. Financial data — SEC XBRL facts via agentii MCP for historical financials
3. Market data — `~~market_data` placeholder for real-time valuation multiples
4. Strategy frameworks — `search_investment_strategies(domain=fundamental, kind=screening)`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (a) Structured Data Query from `contracts/retrieval.md`: primary retrieval via XBRL facts for financial statement data. Supplement with `search_investment_strategies` for screening methodology validation. Detailed methodology in `references/quant-methodology.md`.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements a two-directional screening process: forward-looking valuation discovery and backward-looking financial statement validation. Core principle: the market is mostly efficient. An outlier exists because either the market is wrong (your edge) or you are missing something. Non-participation is always an option.

Detailed methodology: peer selection protocol, turnaround financial scorecard, 7-step sector cleaning, and data mining bias catalog are in `references/quant-methodology.md`.

**Foundational principle**: P/E measures what the market is willing to pay for forward earnings — it is a market psychology metric, not intrinsic value. "Cheap" and "expensive" are not analytical conclusions. The question is: why has the market assigned this multiple? PEG < 1.0 is not a universal buy signal — calibrate sector-relatively, growth-rate-adjust, and cross-check with EV/EBITDA-to-Growth. This skill uses PEG as a *screening filter* only; for a standalone PEG-based valuation, defer to the `peg-valuation` skill.

#### Steps

1. **Universe and Macro Filter**: Apply portfolio bias from orchestrator. Long → $3B-$10B mid-caps. Short → $20B+ large caps. Neutral → both, emphasize pairs. Weight sectors by macro regime preferences.

2. **Forward-Looking Valuation Scan**: Screen using four-pillar framework (PE1, PE2; EG1, EG2; PEG1, PEG2; revenue multiples). Rank by deviation from sector median. Top/bottom decile advance. Calibrate PEG sector-relatively. Use EV/EBITDA-to-Growth as cross-check; prefer EBIT over EBITDA for capital-intensive sectors.

3. **Backward-Looking Financial Validation** (execute in this order):
   - Revenue: growth trajectory, organic vs. acquisition quality, concentration risk
   - Earnings quality: GAAP vs. non-GAAP (> 20% gap = investigate), SBC > 10% revenue = red flag, "non-recurring" in 3+ of 4 quarters = recurring
   - Margin: gross margin trend, incremental margins (> 50% strong, < 20% weak)
   - Cash flow: FCF/Net Income conversion. > 80% excellent, 70-80% acceptable, 50-70% explain, < 50% hard stop for longs. DSO + inventory both rising = channel stuffing risk.

4. **Peer Selection** (dual-path): Sector path (GICS → 10-K competition → sell-side → merger docs) + Fundamentals path (cluster by growth, margins, ROIC). Must converge on 4-6 names. Divergence = classification error. Use median. For a formal benchmarked peer set, hand off to `peer-bench`; for full multiple spreading and calendarization, hand off to `comps` — do not rebuild either here.

5. **Growth Profile and Trap Detection**: EPS CAGR 3-5yr (consistency > magnitude). Estimate trajectory: rising + rising = aligned; falling + rising = danger. Beat/raise = strongest signal. Decompose growth source (revenue vs. cost-cutting vs. buybacks). Turnaround scorecard (0-10): 7-10 investigate long, 0-3 avoid/short. Exclude revenue-growth stories from turnaround classification. Scan for data mining biases.

6. **Sector Cleaning** (when data errors suspected): Apply 7-step protocol from reference. Only clean < 20 candidates that pass initial screen.

7. **Output**: Score each candidate (valuation × validation × growth). Flag GREEN/AMBER/RED. Handoff: ranked list, peer data, turnaround scores, data quality flags.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_quantitative-screening_{affix}.md`

## Output Structure

1. **Executive Summary** — Universe scanned, outliers found, top 5 candidates ranked
2. **Screening Parameters** — Universe, macro filter, metrics used, thresholds
3. **Outlier Results** — Ranked list with valuation metrics, sector comparisons
4. **Financial Validation** — Revenue, earnings quality, margin, cash flow analysis per candidate
5. **Growth Assessment** — EPS trajectory, estimates trend, earnings surprise history
6. **Trap Detection** — Turnaround/value trap flags per candidate
7. **Data Quality Report** — Bias checks, data freshness, caveats
8. **Handoff Summary** — GREEN/AMBER/RED classification with recommended next steps
9. **Coverage Gaps** — Data limitations, missing data points, degraded-mode flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No XBRL data for candidate | Use market data estimates; flag as lower confidence |
| Sector comparison data insufficient | Use broad market medians; flag sector gap |
| `search_investment_strategies` unreachable | Proceed with manual methodology; flag |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/quant-methodology.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`