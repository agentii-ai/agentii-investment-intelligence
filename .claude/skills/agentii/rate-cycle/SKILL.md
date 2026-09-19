---
name: rate-cycle
description: Interest rate cycle analysis, Fed policy analysis, yield curve dynamics, duration management, central bank rate trajectory, monetary tightening easing, bond market analysis, rate forecast, forward curve, dot plot interpretation, rate hike cut cycle
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "8 quarters for rate cycle inflection; 20 for secular rate regime detection."
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
| lookback_quarters | 8 | Captures full rate cycle from hiking to cutting |
| key_indicators | fed_funds, 2s10s_spread, dot_plot, inflation_breakevens | Core rate cycle indicators |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Knowledge entries (L1 rate cycle frameworks) -> 2. search_by_analogue(market_regime: rate-shock) -> 3. Real-time data

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for rate cycle frameworks; query search_by_analogue for historical rate cycles; supplement with real-time data.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Rate Cycle Phase — classify hiking/plateau/cutting/emergency
2. Yield Curve Analysis — 2s10s spread, 3m10y, breakeven inflation
3. Framework Application — Taylor Rule, duration management
4. Analogue Retrieval — past rate cycles matching current phase

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_rate-cycle_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Core Analysis** — applied frameworks with specific evidence
3. **Quantitative Indicators** — key metrics and benchmarks
4. **Historical Analogues** — matched cases with /v/cases/ citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags Rate Cycle Phase 3. Yield Curve Decomposition 4. Central Bank Posture 5. Duration and Curve Positioning 6. Historical Analogues 7. Scenarios

## Error Handling

| Error | Fallback |
|-------|----------|
| No frameworks | Proceed with standard indicators; flag degraded |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/knowledge-frameworks.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
