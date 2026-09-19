---
name: currency-analysis
description: Currency analysis, FX rate forecast, carry trade analysis, purchasing power parity, central bank divergence, currency regime, dollar index DXY, forex strategy, exchange rate modeling, capital flow analysis, currency crisis, peg defense
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "8 quarters for currency cycle; 20 for secular currency regime shifts."
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
| lookback_quarters | 8 | Covers multi-year currency cycles |
| key_indicators | rate_differential, current_account, PPP, reserves | Standard FX valuation framework |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Knowledge entries (L1 currency frameworks) -> 2. search_by_analogue(event_type: currency-peg-break) -> 3. Real-time data

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for currency frameworks; query search_by_analogue for currency crises; supplement with real-time data.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Currency Regime Classification — floating/managed float/pegged/dollarized
2. Fundamental Drivers — rate differential, current account, PPP, terms of trade
3. Framework Application — carry trade, PPP valuation, central bank divergence
4. Analogue Retrieval — past currency crises and regime breaks

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_currency-analysis_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Core Analysis** — applied frameworks with specific evidence
3. **Quantitative Indicators** — key metrics and benchmarks
4. **Historical Analogues** — matched cases with /v/cases/ citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags Currency Regime Classification 3. Fundamental Drivers 4. Central Bank Divergence 5. Historical Currency Crises 6. Scenarios

## Error Handling

| Error | Fallback |
|-------|----------|
| No frameworks | Proceed with standard FX indicators; flag degraded |

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
