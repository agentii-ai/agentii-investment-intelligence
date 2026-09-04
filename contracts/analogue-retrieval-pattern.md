# Analogue Retrieval Pattern — runtime `search_by_analogue`

**Spec**: spec 039 Part I (FR-018/FR-019/FR-023) | **Injected into**: each enriched skill's `## Methodology`

At runtime, an enriched skill discovers relevant spec 037 analogues dynamically (not just the authoring-time curated set in `references/knowledge-frameworks.md`). This keeps recommendations current as the spec 037 corpus grows.

## Call pattern

```
1. Derive analogue tags from the current query domain:
   - market_regime: bubble-mania, crash-capitulation, credit-crunch, melt-up,
     stagflation, deflation-bust, recovery-reflation, range-bound, rate-shock, liquidity-crisis
   - event_type: m&a-strategic, hostile-activist, short-thesis-fraud, regulatory-shock,
     bankruptcy-restructuring, spin-off, earnings-blowup, credit-event, etc.
   - company_situation: distressed-value, hypergrowth, turnaround, cyclical-trough,
     cyclical-peak, melting-ice-cube, hidden-asset, moat-erosion, overleveraged, capital-return-story
2. Call search_by_analogue(market_regime=<regime>, event_type=<event>, company_situation=<situation>,
   layer=<L1|L2|L3|L4>, sector=<sector>, page_size=5).
   Provide at least one of market_regime, event_type, or company_situation.
   Results return BOTH matching cases AND strategies grouped by type.
3. If results: cite each with its /v/ link and weave into the analysis.
4. If empty: state "no relevant historical analogues found" and proceed
   with primary analysis — never fabricate an analogue.
```

## Degraded mode (R1)

If the spec 037 MCP is unreachable, annotate the output with a `coverage_gap`
note ("historical-analogue enrichment unavailable this run") and continue with
the authoring-time `references/knowledge-frameworks.md` set only.

## Citation format

Always the clickable form: `https://agentii.ai/v/{ticker}/{citation_id}/{page}`.
Never the `agentii://` scheme or legacy `/view?ticker=` form (check.py ctx-gate-citation).
