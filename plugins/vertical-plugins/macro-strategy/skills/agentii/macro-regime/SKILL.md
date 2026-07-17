---
name: macro-regime
description: Macro regime analysis, bull bear market detection, business cycle analysis, macro environment assessment, interest rate cycle, yield curve analysis, monetary policy, fiscal policy, global macro, central bank posture, credit cycle, recession probability, expansion regime, macro regime shift, stagflation detection
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "8 quarters (2yr) default lookback to capture cycle inflection points; max 20 for long-cycle detection."
allowed_tools:
  - search_knowledge_entries
  - get_knowledge_entry
  - search_by_analogue
  - get_realtime_quote
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| lookback_quarters | 8 | 2yr captures cycle inflection while remaining responsive |
| regime_indicators | yield_curve, credit_spreads, PMI, VIX, fed_posture | Standard macro regime detection set |
| probability_weighting | bear/base/bull | Three-scenario framework per institutional standard |

## Preflight

Run the canonical pre-flight sequence: MCP health probe, ticker resolution, workspace style override, memory load, and coverage check. See `contracts/preflight.md`. Propagate X-Agentii-Trace header per `contracts/x-agentii-trace-header.md`.

## Data Source Priority (mandatory order)

1. Knowledge entries FIRST — query gold.knowledge_entries for L1 regime frameworks
2. Historical analogues SECOND — query search_by_analogue(market_regime) for matching cases
3. Real-time data LAST — supplemental only

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Query knowledge entries for L1 frameworks via search_knowledge_entries
2. Query search_by_analogue for historical regime precedents
3. Supplement with real-time data

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Regime Detection — classify current macro environment using yield curve, credit spreads, PMI, VIX, Fed posture
2. Framework Application — apply relevant L1 framework from references/knowledge-frameworks.md
3. Analogue Retrieval — query search_by_analogue(market_regime) for historical precedents
4. Probability Weighting — Bear/Base/Bull scenarios with transition catalysts

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_macro-regime_{affix}.md`

## Output Structure

1. Executive Summary — current regime with probability weights
2. Regime Indicators — yield curve, credit spreads, PMI, VIX with readings
3. Framework Analysis — applied L1 frameworks with evidence
4. Historical Analogues — matched cases with /v/cases/ citations
5. Scenario Matrix — Bear/Base/Bull with catalysts
6. Risk Factors and Coverage Gaps

## Error Handling

| Error | Fallback |
|-------|----------|
| No L1 frameworks | Proceed with standard indicators; flag degraded |
| search_by_analogue empty | Note no analogue found; do not fabricate |
| Real-time quote unavailable | Use last-known values with staleness flag |

## Memory Load

Load prior context before retrieval. See `contracts/memory-load.md`.

## Snapshot

Post-session synthesis. See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs for cited frameworks and cases.

## References

- `references/knowledge-frameworks.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
