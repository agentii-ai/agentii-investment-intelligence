# Med Knowledge Frameworks (shared)

Full regulatory grounding lives in the fda-catalyst-analysis skill's reference:
`../../fda-catalyst-analysis/references/knowledge-frameworks.md` (FDA/EMA process,
AdCom mechanics, six scrutiny axes, catalyst sizing, med metrics).

## 道/法 layered review knowledge (runtime retrieval)

Retrieve at runtime via `search_investment_strategies(sectors=med, layer_tags=L2)`
and cite with /v/ URLs:
- 道 (L1): Substantial Evidence Standard · Totality of Evidence & Benefit-Risk
  Balance · Safety Signal Characterization · Patient-Centric Risk-Benefit
  Context · Clinical Meaningfulness of Endpoints
- 法/器 (L2): Comparator Selection Adequacy · Missing Data Sensitivity ·
  Subgroup Consistency · Surrogate Endpoint Validation · RWE Credibility ·
  REMS Effectiveness · Trial Design Integrity · Vote Tally Interpretation
  Matrix · Red Flag Screening Checklist

## Structured AdCom calendar

`search_adcom_meetings` (committee/product/ticker/date/vote filters,
122 meetings, 113 with votes) + `get_adcom_meeting` (briefing-doc inventory).

## Cross-Trial Comparison Lattice

- Every readout is placed against **standard of care and same-class peers** on aligned endpoints — efficacy, tolerability, and persistence columns per comparator. A readout judged in isolation misses the class context that sets the bar.
- Comparator rows carry the trial name, endpoint definitions, and sample context; where a comparator did not measure an aligned endpoint, the cell is marked unavailable, never guessed.
- The lattice answers "better than what?" before it answers "good enough?" — the two questions are different and both required.

## Tolerability / Persistence Axis

- Tolerability/persistence is a **co-equal axis to efficacy**, not a secondary read: discontinuation rates, dose reductions, and AE-driven dropout frequently decide commercial uptake even when efficacy is superior.
- The axis is read per arm and per timepoint; a headline efficacy win with a materially worse dropout curve is scored accordingly.
- Titration burden and dosing convenience feed the same axis — persistence is a behavior, not just a safety stat.

## Safety-Imbalance Deferral

- A safety imbalance observed at readout scale defers the verdict to a **larger outcomes trial**; small-N imbalances are reported, not over-weighted.
- The deferral is explicit in the output ("verdict deferred to [outcomes trial]"), and the readout's own conclusions are limited to what its power supports.
- Never extrapolate a safety signal beyond the trial's size and duration; the discipline is to wait for scale, not to extrapolate from it.

## Materiality-Rated Conflict Handling

- Conflicting characterizations of the same data are surfaced **verbatim** (both readings, with sources), then **rated by materiality** ("incremental positive, not narrative-changing") or **deferred** to a larger outcomes trial when the design cannot settle the question.
- Conflicts are never silently averaged; an unresolved conflict stays flagged as unresolved and travels with the conclusion.
- Materiality ratings reference model impact: a conflict that changes estimates is material; one that changes only framing is incremental.
