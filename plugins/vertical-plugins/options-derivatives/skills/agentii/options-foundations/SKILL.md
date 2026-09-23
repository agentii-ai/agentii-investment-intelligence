---
name: options-foundations
description: options foundations, Greeks analysis, volatility surface, put call parity, options pricing, delta gamma theta vega rho, Black Scholes, options theory, derivatives basics, options mechanics
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters for option position analysis; 12 for volatility regime comparison."
allowed_tools: [search_knowledge_entries, get_knowledge_entry, search_by_analogue, get_realtime_quote]
retrieval_scope: structured_only
min_tool_diversity: 4
parameter_free: true
---

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| parameter_free | true | This skill has no tunable parameters; analysis scope set by temporal_scope frontmatter |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md` — carry the `_run_id` from your first tool result and name yourself (and your parent, if you were spawned).

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for relevant frameworks; query search_by_analogue for historical cases.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
See ## Protocol section below.



# Options Foundations

Options analysis powered by spec 037 L3/L4 knowledge base (K7).

## Preflight
Run the canonical pre-flight sequence. See `contracts/preflight.md`.

## Data Source Priority
1. Knowledge entries (K7 options frameworks) → 2. `search_by_analogue` for relevant cases

**The options-chain input does not exist, and this skill must say so (spec 058 FR-028).** No route and no
MCP tool on this deployment returns an option chain — `get_options_chain` is implemented nowhere, and this
skill no longer declares it. So chain-derived quantities (bid/ask, open interest, per-strike Greeks,
implied volatility by strike) have **no source**. They MUST NOT be presented as retrieved, estimated from
the underlying's price, or reconstructed from memory. Name the missing input in the artifact, annotate
`coverage_gap` per `contracts/error-handling-template.md`, and abstain from the parts of the analysis that
depend on it. What remains is real: K7's frameworks apply to a name without a chain.

## Protocol
1. **Framework Application** — apply K7 frameworks from `references/knowledge-frameworks.md`
2. **Option Chain Analysis** — **abstain**, and say why: no tool returns an option chain (see Data Source Priority). Apply the K7 frameworks and list the chain inputs that were unavailable instead of inferring them.
3. **Analogue Retrieval** — query historical options/volatility cases

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query gold.knowledge_entries for frameworks; query search_by_analogue for historical cases.

### Temporal Scope
See frontmatter temporal_scope.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
See ## Protocol section below.

## Output File
`{ticker}/{YYYY-MM-DD_HHMM}_options-foundations_{affix}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Framework Analysis** — applied frameworks with specific findings
3. **Quantitative Metrics** — relevant calculations and benchmarks
4. **Historical Analogues** — matched cases with citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags
1. Executive Summary 2. Framework Analysis 3. Option Greeks & Metrics 4. Historical Analogues 5. Risk Profile 6. Scenarios

## Error Handling
| Options chain input — **no tool provides one** (`get_options_chain` is unimplemented; FR-028) | Framework-only analysis; name the missing input in the artifact and annotate `coverage_gap`. Never present chain-derived figures as retrieved. |

## Final Summary (TUI)
Include `### Key Citations` block (0–10 /v/ URLs).

## Memory Load

Load prior context before retrieval. See `contracts/memory-load.md`.

## Snapshot

Post-session synthesis. See `contracts/snapshot-synthesis.md`.

## Output Frontmatter

Structured output per `contracts/output-frontmatter-schema.md`.

## References
`references/knowledge-frameworks.md`, `contracts/citation-and-memory.md`
