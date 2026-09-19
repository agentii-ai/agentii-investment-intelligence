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

## What's-changed vectors & model-vs-consensus deltas (earnings preview)

- **Three what's-changed vectors**: every preview closes by slot-refreshing
  three vectors — estimates (what numbers moved and why), thesis (what the
  quarter does to the investment case), positioning (where investor attention
  sits and the per-name bull/bear pivot conditions). Slot-refresh order:
  estimates move first; thesis and positioning follow only when the facts
  justify them.
- **Model-vs-consensus deltas**: each key line item states our modeled number
  against the consensus value pulled from `search_earnings_calendar`, with the
  delta signed and the driver named. Where no consensus value is retrievable,
  the delta degrades to a `coverage_gap` with the required-input list — never
  a fabricated comparison.
- **Uncertainty discipline**: scenario-flexing stays at market level, POS at
  asset level (peak × POS, changes logged with reasons); explicit abstention
  where a swing factor is unquantifiable.
- **Buy-side lens**: client-question framing ("one common question we have
  received"); per-name bull/bear pivot conditions stated, not implied.
