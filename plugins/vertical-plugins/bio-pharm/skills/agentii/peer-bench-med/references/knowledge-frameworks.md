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

## Launch-analog matching & mechanism-overlap scoring (peer selection)

- **Science-first peer logic**: med peers are defined by what they develop,
  not by industry codes — indication/drug overlap comes first, financial
  comparison second.
- **Same-class, same-channel analog matching**: for commercial-stage names,
  match launch analogs on two axes — class (mechanism/indication class, so
  launch curves are comparable) and channel (specialty pharmacy, retail
  pharmacy, hospital/IV administration, device-rep detail, vaccine
  procurement) — because channel drives both gross-to-net economics and launch
  slope. A peer without a named analog set is flagged.
- **Mechanism-overlap scoring**: for each key indication and molecular target
  of the subject company, run the drug-knowledge reverse lookups
  (`search_drugs_by_indication`, `search_drugs_by_target`); score each
  candidate peer by its count of shared targets/indications and rank the comp
  set on that score. Where two sources disagree on a drug's mechanism, both
  values are kept with provenance — never silently merged.
- **Analogs as benchmarks**: ≥2 named same-class analogs per commercial-stage
  peer where launch history exists; the analog overlay is the yardstick for
  launch trajectories, not a post-hoc narrative.
