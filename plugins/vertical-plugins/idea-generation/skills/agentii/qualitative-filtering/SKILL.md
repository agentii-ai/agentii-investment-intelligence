---
name: qualitative-filtering
description: Qualitative stock analysis, management operating plan MOP assessment, key performance indicator KPI identification, catalyst identification and classification, earnings call transcript analysis, qualitative evidence gathering for investment thesis
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Catalyst identification requires forward visibility; 4 quarters default."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
  - search_investment_cases
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
| catalyst_window_days | 20-60 | Trading horizon for active positions |
| kpi_trend_min_quarters | 8 | Minimum quarters of KPI history for trend analysis |
| mgmt_track_record_years | 3 | Management credibility requires 3+ years of guidance vs actuals |
| catalyst_min_impact | 5% | Minimum expected price impact to justify catalyst-driven trade |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Qualitative methodology — `references/qual-methodology.md` (bundled MOP-KPI-Catalyst framework)
2. Company disclosures — SEC filings (Business Description, Risk Factors, MD&A) via agentii MCP
3. Earnings transcripts — defeatbeta-api via `~~earnings_data` placeholder
4. Strategy and case knowledge — `search_investment_strategies` + `search_investment_cases` + `search_by_analogue`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (d) Simple Lookup from `contracts/retrieval.md`: the qualitative framework is bundled in `references/qual-methodology.md`. Earnings transcripts from data tools. Strategy frameworks and historical analogues via MCP knowledge tools. Detailed methodology and catalyst classification in `references/qual-methodology.md`.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill implements qualitative investment analysis through a three-stage framework: MOP → KPI → Results. Companies do not publish an "MOP" — the analyst infers it by identifying KPIs first, then reverse-engineering the strategic plan. The analyst verifies the chain is intact and credible. A broken chain is the highest-quality short signal.

Detailed methodology: management assessment framework (Alpha/Beta/Delta), board quality checklist, mosaic theory triangulation, catalyst taxonomy, sector-specific KPI templates, and the 20+ pattern red flag catalog are in `references/qual-methodology.md`.

**Critical distinction**: Good company ≠ good stock. For the 20-60 day horizon, catalysts are required.

#### Steps

1. **KPI Identification**: Identify industry-specific KPIs per the reference templates (SaaS, retail, manufacturing, financial services, healthcare). Determine leading vs. lagging. Assess consistency (changing KPIs = red flag), auditability, relevance. Map trends over 8+ quarters. KPI divergence from sector norms often explains quantitative outlier signals.

2. **MOP Analysis** (5-dimension scorecard, each 0-10, composite < 25 = high risk): Extract from earnings calls, presentations, MD&A. Infer the MOP: forward-looking statements → recurring themes → strategic narrative → test consistency/credibility. Score on: Track Record (30%, 3yr+ guidance vs. actuals), Consistency (20%), Realism (20%), Alignment (15%, insider ownership + compensation structure), Disclosure Quality (15%). Red flags: transformational M&A without plan, repeated guidance misses, high SBC with low hurdles, C-suite turnover within 18 months.

3. **Management Team** (Alpha/Beta/Delta): Alpha (CEO) — track record, capital allocation, communication style. Primary Betas (CFO, CPO, CTO, Corp Dev, CMO) — depth and tenure. Red flags: cluster departures, CFO departure near guidance, cluster insider selling.

4. **Board Assessment**: Independence ≥ 75%, expertise present, financial expert on audit committee. "Political incest" check: management/board overlap. Red flags: classified board, supermajority voting, tenure > 15yr, CEO as Chair, related-party transactions.

5. **Industry Analysis**: Five Forces and SWOT as thinking prompts, not rigid boxes. Read competitor 10-Ks to cross-check management narrative. Do not trust management pronouncements on competition — verify independently. "Explain to 10-year-old" test: describe in 1-2 sentences. "3-5 factors" rule: identify drivers that matter; more than 5 = spread too thin. For formal peer-set construction and relative benchmarking, defer to the `peer-bench` skill rather than rebuilding it here.

6. **Consensus Reconstruction** (run *after* steps 1-5, never before — reading consensus early anchors the analysis to the expectation it is meant to test): Establish the published sell-side average **and its dispersion**, then triangulate the effective buy-side expectation, which typically moves ahead of the published figure. Weight recent revisions over the stale average. Output a range with a direction, never a point estimate. Wide dispersion = no consensus exists, so the disconnect framing does not apply; tight dispersion with stale revisions is the highest-value setup. If the buy-side bar cannot be triangulated, mark the disconnect **unquantified** and flag a coverage gap rather than substituting the published number. State the variant view as: market expects X, evidence indicates Y, because [KPI/MOP finding], closing when [catalyst] by [date].

7. **Catalyst Identification**: Identify all catalysts within 20-60 days. Classify: Earnings / Corporate Action / Regulatory / Management / Industry / Macro. Assess: specificity (dateable?), magnitude (≥ 15% high, 5-15% standard, < 5% insufficient), probability, binary vs. spectrum (binary → reduce size). Tumbleweed test: < 1 non-earnings press release/month = avoid. Catalyst stacking: multiple = higher conviction; zero = investment, not trade.

8. **Red Flag Scan**: Scan against catalog (see reference). 3+ flags = hard stop for longs. Key flags: non-recurring charges in 3+ of 4 quarters, SBC > 10% revenue, GAAP losses + non-GAAP profits, trade data contradicts management, competitor filings describe different dynamics.

9. **MCP Integration**: `search_investment_strategies(kind=qualitative)` → `search_investment_cases(domain=catalyst_driven)` → `search_by_analogue(event_type, company_situation)`. Handoff: conviction score (1-10), quantified consensus disconnect (or `unquantified`), ranked catalyst calendar, KPI summary, MOP score, management/board flags, red flag count.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_qualitative-filtering_{affix}.md`

## Output Structure

1. **Executive Summary** — Qualitative conviction level, key catalyst, MOP credibility rating
2. **KPI Analysis** — Industry-specific KPIs, trend assessment, leading vs. lagging classification
3. **MOP Assessment** — Management strategy, credibility evaluation, red flags, track record
4. **Business Quality** — Competitive position, industry dynamics, product/service assessment
5. **Consensus Disconnect** — Published sell-side average and dispersion, triangulated buy-side range with direction, the quantified gap (or `unquantified`), and the variant view in one structured sentence
6. **Catalyst Calendar** — All identified catalysts with type, date, expected impact, probability
7. **Earnings Call Analysis** — Key takeaways from recent transcripts, management tone, analyst sentiment
8. **Qualitative Red Flags** — Governance concerns, strategy pivots, disclosure quality issues
9. **Knowledge Integration** — Matched strategies and historical analogues with /v/ citations
10. **Handoff Summary** — Conviction score, priority catalyst, recommended next step (template/proceed/watch)
11. **Coverage Gaps** — Data limitations, degraded-mode annotations

## Error Handling

| Error | Fallback |
|-------|----------|
| No earnings transcript available | Use SEC filings only; flag transcript gap |
| No catalyst within 60-day window | Flag as watchlist item; do not force a catalyst |
| `search_by_analogue` returns empty | Note "no relevant analogues found"; do not fabricate |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/qual-methodology.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`