---
name: trade-idea-generation
description: Systematic trade idea generation framework, fundamental quantitative and qualitative screening pipeline, catalyst-driven trade structuring, macro-to-micro idea translation, 20-60 day long-short portfolio management process
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "20-60 trading day horizon for trade idea generation; up to 12 quarters for macro context."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
  - search_investment_cases
  - get_investment_case
  - search_by_analogue
retrieval_scope: structured_only
layer_tags: ["L2", "L3"]
min_tool_diversity: 3
parameter_free: false
---

> Methodology fused from professional trading and investment frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| trade_horizon_days | 20-60 | Professional long/short portfolio management sweet spot |
| volatility_target | 20% annualized | Target portfolio volatility (1.5-2x VIX) |
| screening_universe | S&P 500 + liquid mid-caps | Default screening universe for trade ideas |
| portfolio_bias_source | macro-analysis skill | Derive bias from upstream macro view |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Process framework — embedded in this Protocol (proprietary systematic process)
2. Quantitative data — `search_investment_strategies` + financial data from market data scripts
3. Qualitative context — `search_investment_cases` + `search_by_analogue` for historical analogues
4. Real-time context — market conditions and sector trends from data tools

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
**Ownership & insider signals**: `search_institutional_holdings` (top-10 holders + whale portfolios, `direction=accumulating|reducing|new|exited`) and `search_insider_trades` (Form-4 transactions with SEC URLs) are available as signal inputs.

This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: query `search_investment_strategies` for fundamental analysis frameworks, `search_investment_cases` for historical case analogues, `search_by_analogue` for cross-strategy discovery. Delegates detailed analysis to sub-skills. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill orchestrates a systematic trade idea generation pipeline for the 20-60 day long/short portfolio management horizon. Detailed methodology, funnel architecture, composite scoring, operational cadence, and the trade-vs-investment hard gate are in `references/pipeline-orchestration.md`.

**Core formula**: Trade Idea = Fundamentals + Timing + Trade Structure. If any component is missing, the idea is not actionable.

**Hard gate**: A trade idea requires a specific, dateable catalyst within 20-60 days. Without one, the idea is an investment, not a trade — move to watchlist.

**Pipeline funnel** (6 gates, see reference for thresholds):
```
Universe → Gate 1: Quant Screen → Gate 2: Financial Validation → 
Gate 3: Qualitative Filter → Gate 4: Template Assembly → 
Gate 5: Strategy Match → Gate 6: Trade Structure → Pipeline Ranking
```
Composite: (Quant × 0.30) + (Qual × 0.30) + (Catalyst × 0.25) + (Macro × 0.15), each 1-10.

#### Phase 1 — Theory

1. **Macro Bias Input**: Receive portfolio bias (long/short/neutral) from upstream. Long → $3B-$10B mid-caps. Short → $20B+ large caps (never short mid-caps — takeover risk). Neutral → emphasize pair trades. Assess sector tailwinds/headwinds.
2. **Quantitative Screening**: Delegate to `quantitative-screening`. Inputs: bias, sectors, universe. Outputs: ranked outlier list, financial validation, growth profiles, trap classification, data quality flags.
3. **Qualitative Deep Dive**: Delegate to `qualitative-filtering` for top <10 candidates. Inputs: candidate list, metrics, sector context. Outputs: KPI analysis, MOP credibility (5-dimension scorecard), management/board assessment, catalyst calendar with specificity/magnitude/probability.
4. **Template Assembly**: Delegate to `trade-template`. Inputs: all quant/qual outputs, macro, peer data. Outputs: multi-method price targets, probability-weighted scenarios (Base 55/Bull 20/Bear 25), GAAP reconciliation, thesis statement.
5. **Macro-Driven Cases**: Delegate to `macro-idea-generation` for top-down ideas. Inputs: regime, indicators, international context. Outputs: regime-to-sector mapping, macro catalyst timeline, ADR candidates, invalidation thresholds.

#### Phase 2 — Implementation

6. **Strategy Matching**: `search_investment_strategies(domain=fundamental)` → `search_by_analogue(company_situation, event_type)` → `get_investment_strategy`. Cross-reference: do matched strategies confirm or challenge the thesis?
7. **Historical Precedent**: `search_investment_cases(domain=[derived])`. Flag parallels and divergences. Cite via `/v/` links. Note gaps explicitly — absent precedent is itself information.
8. **Trade Structure**: Stock (default), options (delegate to `options-execution`), or pair trade (market-neutral, macro divergence). Requirements: identifiable catalyst within 60 days, R/R > 2:1.
9. **Pipeline Output**: Rank by composite. Classify: Actionable (all gates, catalyst < 60d, R/R > 2:1) / Watchlist (catalyst > 60d, R/R borderline) / Discard (failed gates 1-3). Document full audit trail.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_trade-idea-generation_{affix}.md`

## Output Structure

1. **Executive Summary** — Pipeline funnel statistics (universe → gate 1 → ... → gate 6 counts), composite scores, top 3 actionable recommendations
2. **Macro Context** — Portfolio bias (long/short/neutral), macro regime, sector tailwinds/headwinds
3. **Quantitative Screening Results** — Outlier list with sector-relative metrics, peer groups, financial validation flags, data quality report
4. **Qualitative Filtering Results** — KPI analysis, MOP credibility scores, management/board assessments, catalyst calendar with quality ratings
5. **Trade Templates** — Full templates for top candidates: price targets (all three methods with weights), trading comps output, GAAP reconciliation, scenario analysis
6. **Strategy Framework Matches** — Matched strategies from knowledge base with `/v/` citations, confirmation or challenge to thesis
7. **Historical Analogues** — Matched cases with parallels/divergences analysis, key learnings from precedent
8. **Trade Structure Recommendations** — Stock/options/pair trade decisions with catalyst timelines and R/R ratios
9. **Prioritized Pipeline** — Ranked watchlist with composite scores, conviction levels, position sizes, classification (Actionable/Watchlist/Discard)
10. **Audit Trail** — Full documentation from macro bias → screen → filter → template → strategy → structure
11. **Coverage Gaps** — Data limitations, degraded-mode annotations, candidates flagged for further research

## Error Handling

| Error | Fallback |
|-------|----------|
| No macro bias input | Run with neutral bias; screen both directions; flag missing context |
| Quantitative screening returns empty | Broaden screening parameters; check data sources; flag |
| No strategy frameworks found | Proceed with manual analysis; flag knowledge base gap |
| `search_by_analogue` empty | Note "no relevant historical analogues found"; do not fabricate |
| Sub-skill unavailable | Execute steps manually using embedded framework; flag degraded |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/pipeline-orchestration.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`