---
name: long-short-equity
description: long short equity strategy, pair trade construction, market neutral portfolio, net exposure management, factor neutrality, equity long short, hedge fund strategy, alpha generation, stock picking portfolio construction, long short position management
multi_ticker_semantics: target_with_optional_peers
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "8 quarters for portfolio construction; 20 for strategy backtesting."
allowed_tools: [search_investment_strategies, get_investment_strategy, search_investment_cases, search_by_analogue, get_realtime_quote, search_xbrl_facts]
retrieval_scope: structured_only
layer_tags: ["L3"]
min_tool_diversity: 4
parameter_free: true
---

> Methodology fused from institutional long/short and buy-side research frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| parameter_free | true | This skill has no tunable parameters; analysis scope set by temporal_scope frontmatter |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Strategy methodology — `references/strategy-methodology.md` (bundled long/short framework)
2. Strategy frameworks — `search_investment_strategies(domain=fundamental)`
3. Historical precedent — `search_investment_cases` + `search_by_analogue(company_situation=...)`
4. Financials — `search_xbrl_facts` for unit economics and decline-rate evidence

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (a) Structured Data Query from `contracts/retrieval.md`. Retrieve frameworks via `search_investment_strategies`, precedent via `search_investment_cases` and `search_by_analogue`. Detailed methodology in `references/strategy-methodology.md`.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

Every long/short position rests on an **earnings disconnect** — a gap between what the market
has priced and what the business will deliver. The unifying question across all strategy
types is: what does consensus believe, and what do I believe differently? Strategy
spectrum, short archetypes, and process detail are in `references/strategy-methodology.md`.

**Consensus is not the published number.** Sell-side consensus is a simple average of
analyst estimates; buy-side consensus typically moves ahead of it. Trading against the
published figure while the real positioning has already shifted is a common and expensive
error. Triangulate the effective buy-side expectation before sizing any view.

#### Steps

1. **Strategy Classification**: Place the idea on the spectrum from spread-focused to
   fundamentals-focused — merger arbitrage (0-18mo), general event-driven (0-24mo), activist
   (0-24mo), value/deep value (0-5yr+), growth or growth-at-reasonable-price (0-5yr+). The
   classification sets the expected holding period and the evidence bar. Categories overlap;
   record the dominant driver rather than forcing a single label.

2. **Consensus Reconstruction**: Establish the published sell-side figure, then estimate the
   effective buy-side expectation. Document the gap and its direction — the disconnect is
   the position, not the absolute valuation level.

3. **Idea Provenance**: Record how the idea was sourced — industry research and trade events,
   tangential analysis of adjacent markets, practitioner conversations, curated research
   communities, or quantitative screens. Provenance predicts which failure modes to test
   for: screen-sourced ideas need qualitative validation, conversation-sourced ideas need
   independent quantitative confirmation.

4. **Long-Side Thesis**: Apply value or growth frameworks per classification. Value requires
   a discount to net present value on a price basis; growth requires a discount on an
   earnings basis. State which, and why the market has mispriced it.

5. **Short-Side Archetype** (when shorting): Classify into one of three patterns —
   **competition short** (complacent incumbent facing a credible new entrant; test the
   entrant's unit economics and assess whether incumbent management can and will react),
   **consumer euphoria** (a product with outsized enthusiasm that will not sustain; test via
   market sizing and product work), or **disappearing business** (an incumbent in a
   structurally terminal market; establish the rate of decline, the cash-flow profile during
   decline, and whether cash can be redeployed). Each archetype has a distinct evidence
   requirement — do not substitute a valuation opinion for the archetype test.

6. **Precedent Retrieval**: Query `search_by_analogue` for the matching situation and
   `search_investment_cases` for outcome history. Weight precedent by archetype match, not
   sector match.

7. **Risk and Invalidation**: Name what would falsify the thesis and by when. For shorts,
   additionally record borrow availability, short interest, and days-to-cover — a correct
   short thesis in a crowded, hard-to-borrow name is not an executable position.

8. **Output**: Deliver the classification, the quantified disconnect, the archetype evidence,
   precedent with /v/ citations, and explicit invalidation conditions.

## Output File
`{ticker}/{YYYY-MM-DD_HHMM}_long-short-equity_{affix}.md`

## Output Structure

1. **Executive Summary** — strategy classification, the disconnect, and direction in 2-3 sentences
2. **Strategy Classification** — position on the spread-to-fundamentals spectrum with expected holding period
3. **Consensus Disconnect** — published sell-side figure vs estimated buy-side expectation, with the gap quantified
4. **Idea Provenance** — sourcing route and the failure modes it implies
5. **Thesis Detail** — long-side value/growth basis, or short-side archetype with its specific evidence test
6. **Historical Analogues** — archetype-matched precedent with /v/ citations
7. **Executability** — for shorts: borrow, short interest, days-to-cover
8. **Risk and Invalidation** — falsification conditions and deadline
9. **Coverage Gaps** — data limitations and degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No strategy frameworks available | Proceed with `references/strategy-methodology.md`; flag `knowledge_coverage: degraded` |
| Buy-side consensus cannot be triangulated | Report the sell-side figure only and mark the disconnect as unquantified |
| Borrow / short-interest data unavailable | Mark the short as not executability-cleared; do not present it as actionable |
| `search_by_analogue` returns empty | Continue without precedent; annotate `coverage_gap` |

## Final Summary (TUI)
Include `### Key Citations` block (0–10 /v/ URLs).

## Memory Load

Load prior context before retrieval. See `contracts/memory-load.md`.

## Snapshot

Post-session synthesis. See `contracts/snapshot-synthesis.md`.

## Output Frontmatter

Structured output per `contracts/output-frontmatter-schema.md`.

## References

- `references/strategy-methodology.md`
- `references/knowledge-frameworks.md`
- `contracts/citation-and-memory.md`
- `contracts/retrieval.md`
- `contracts/preflight.md`
