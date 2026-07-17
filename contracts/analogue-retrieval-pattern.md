# Analogue Retrieval Pattern — runtime `search_by_analogue`

**Spec**: spec 039 Part I (FR-018/FR-019/FR-023) | **Injected into**: each enriched skill's `## Methodology`

At runtime, an enriched skill discovers relevant spec 037 analogues dynamically (not just the authoring-time curated set in `references/knowledge-frameworks.md`). This keeps recommendations current as the spec 037 corpus grows.

## Call pattern

```
1. Derive the analogue axis from the current query domain:
   - valuation / financials    → axis = "strategy"
   - competitive / positioning → axis = "case"
   - price-action / technical  → axis = "setup"
2. Call search_by_analogue(target=<ticker>, axis=<axis>, top_k=3).
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
