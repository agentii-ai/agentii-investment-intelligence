---
name: long-short-construction
description: Long short portfolio construction, market neutral positioning, factor-balanced book, gross and net exposure management, pair selection, beta hedging, portfolio construction methodology
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters default for long-short-construction analysis; up to 12 for regime context."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
  - search_investment_cases
  - search_by_analogue
retrieval_scope: structured_only
layer_tags: ["L3"]
min_tool_diversity: 3
parameter_free: false
---

> Methodology fused from institutional portfolio-construction and buy-side long/short frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| lookback_quarters | 4 | Standard window for beta and correlation estimation |
| gross_exposure_target | 150% | Mid-range of the 130-200% institutional band |
| net_exposure_band | -20% to +60% | Defines strategy identity; outside this is style drift |
| beta_net_deviation_max | 15pp | Gap between raw and beta-adjusted net above which the hedge is mis-specified |
| max_long_position | 5% | Standard conviction sizing |
| max_short_position | 3% | Halved for unbounded loss and adverse position drift |
| max_days_to_cover | 5 | Squeeze avoidance on any single short |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Construction methodology — `references/construction-methodology.md` (bundled exposure framework)
2. Strategy frameworks — `search_investment_strategies(domain=fundamental, kind=position_sizing)`
3. Historical analogues — `search_by_analogue(market_regime=...)` for regime-specific exposure precedent
4. Market data — `~~market_data` placeholder for beta estimation and borrow/short-interest inputs

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (a) Structured Data Query from `contracts/retrieval.md`. Retrieve construction frameworks via `search_investment_strategies`; retrieve regime precedent via `search_by_analogue`. Detailed methodology in `references/construction-methodology.md`.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

Gross and net exposure are **two independent dials**. Gross sets how much stock-specific
opportunity the book harvests; net sets how much of the return is simply the market.
Raising gross while holding net constant is the defining move of long/short construction —
it is what separates the strategy from levered long-only. Full derivations, attribution
worked examples, and book-level limit tables are in `references/construction-methodology.md`.

**Foundational principle**: return tracks **net** exposure, not gross. Adding equal-beta
shorts to a long book halves the return without improving selection. A short book that
exists only to damp beta is a pure drag — shorts must earn their own alpha, or index-level
hedging is the cheaper and more honest instrument.

#### Steps

1. **Exposure Inventory**: Compute long %, short %, gross (L+S), and raw net (L−S) against
   NAV. Record the starting point before any proposed change.

2. **Beta-Adjusted Net** (the decision-grade measure): Compute
   `(Long% x weighted long beta) - (Short% x weighted short beta)`. Raw net silently assumes
   both sides share market sensitivity. High-beta growth longs hedged with defensive
   low-beta shorts can carry *more* directional risk than raw net implies. If raw and
   beta-adjusted net diverge by more than `beta_net_deviation_max`, the hedge is
   mis-specified — re-select or re-size the short side rather than reporting raw net.

3. **Risk Decomposition**: Confirm the book's residual is idiosyncratic. Market components
   offset across paired exposure, leaving long-side plus short-side company/industry risk.
   Note the failure mode explicitly: with beta removed there is no tailwind to carry weak
   selection.

4. **Short-Side Classification**: Separate **alpha shorts** (held to earn a return on their
   own thesis) from **index shorts** (held to damp beta). These are not interchangeable —
   using alpha shorts as a beta hedge pays the analytical cost of the former for the return
   profile of the latter. Screen every alpha short against the seven structural constraints
   (market long bias, unbounded loss, timing, borrow availability, short interest and
   days-to-cover, volatility asymmetry, sizing).

5. **Position Drift Check**: Short weights move adversely by construction — a losing short
   grows into the book while a losing long shrinks out of it. Schedule re-sizing rather than
   relying on stops alone. Flag any short exceeding `max_short_position` or
   `max_days_to_cover`.

6. **Pair Integrity** (when expressing an explicit pair): same primary risk factor on both
   legs; beta-match rather than dollar-match; each leg must clear the research bar
   independently; name the divergence catalyst and its date range; size for the decoupled
   case, since correlated legs decouple precisely under the stress the pair was built to
   survive.

7. **Sensitivity Grid**: Publish fund return across a −20% to +20% market range. The slope
   of the row **is** net exposure; the intercept **is** alpha. Diagnose both separately — a
   book can post a good return while its intercept is zero and its slope is merely large.

8. **Limit Reconciliation**: Check gross, net band, sector net, and per-position sizes
   against Defaults. Recompute all three exposure measures after every position change; the
   two dials stay independent only if measured continuously, otherwise a series of
   individually reasonable trades silently converts a hedged book into a levered
   directional one.

9. **Output**: Report both exposure measures, the attribution split (beta contribution vs
   alpha contribution per side), the sensitivity grid, and every limit breach.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_long-short-construction_{affix}.md`

## Output Structure

1. **Executive Summary** — current gross/net/beta-adjusted net and whether the book sits within its mandate band
2. **Exposure Table** — long %, short %, gross, raw net, beta-adjusted net, with weighted betas per side
3. **Attribution Split** — beta contribution vs alpha contribution for the long and short books separately
4. **Short-Side Review** — alpha vs index classification, seven-constraint screen, days-to-cover and borrow status
5. **Pair Detail** — per-pair legs, beta match, divergence catalyst and expected window
6. **Sensitivity Grid** — fund return across −20% to +20% market range, with slope (net) and intercept (alpha) called out
7. **Limit Reconciliation** — every Defaults threshold with pass/breach status
8. **Historical Analogues** — regime-matched exposure precedent with /v/ citations
9. **Coverage Gaps** — missing betas, unavailable borrow data, degraded-mode flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No beta data for a holding | Use sector-median beta; flag the substitution and widen the reported beta-adjusted net as a range |
| Borrow / short-interest data unavailable | Report the short as unverified for squeeze risk; do not clear it against `max_days_to_cover` |
| `search_investment_strategies` unreachable | Proceed with `references/construction-methodology.md`; annotate `coverage_gap` |
| `search_by_analogue` returns empty | Continue without regime precedent; flag reduced confidence on the exposure band |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/construction-methodology.md`
- `contracts/citation-and-memory.md`
- `contracts/retrieval.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
