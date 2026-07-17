---
name: price-action-options
description: Options price action strategy, volatility-aware entries, options structure selection by market regime, delta and gamma positioning, options overlay on directional views, expiry selection
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters default for price-action-options analysis; up to 12 for regime context."
allowed_tools:
  - search_knowledge_entries
  - get_knowledge_entry
  - search_by_analogue
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught trading frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| lookback_quarters | 4 | Standard window for price-action-options |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Knowledge entries (frameworks) -> 2. search_by_analogue for historical analogues -> 3. Real-time context

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for price-action-options frameworks; query search_by_analogue for historical analogues.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Framework selection
2. Signal analysis
3. Analogue retrieval
4. Risk assessment

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_price-action-options_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Core Analysis** — applied frameworks with specific evidence
3. **Quantitative Indicators** — key metrics and benchmarks
4. **Historical Analogues** — matched cases with /v/ citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags

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

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
