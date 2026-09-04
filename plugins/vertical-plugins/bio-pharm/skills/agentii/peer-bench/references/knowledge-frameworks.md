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
