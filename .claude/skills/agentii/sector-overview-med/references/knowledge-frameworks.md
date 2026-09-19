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

## Cross-Sector Ripple Map

- For every sector-level catalyst, propagate a **quantified sign and magnitude per covered name** — the have/have-not stock map. A sector view that stops at the headline is incomplete.
- Ripple logic: a class readout, pricing action, or FDA decision moves each name by its exposure — names with positive exposure carry a + sign and an estimated magnitude, names with negative exposure a −, and names with no exposure are listed as have-nots rather than omitted.
- Magnitudes are either sourced or labeled `[VIEW]`; a magnitude without a source or label is a defect.
- The map ranks names by magnitude of exposure, so attention flows to the names the catalyst actually moves.

## Living-Exhibit Convention

- Sector exhibits are **append-only**: each new observation appends to the existing exhibit with its date and source line; prior entries are never rewritten.
- Rewriting destroys the audit trail that makes a sector view verifiable over time; an updated view is a new entry, not an edit of an old one.
- Holiday and event-date labels travel with the entry so a later reader can judge the reading against the calendar.
