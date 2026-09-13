---
name: trial-readout-analysis
description: "Clinical-trial readout analysis: pull the trial, evaluate the readout with AdCom-style scrutiny (endpoints, statistics, subgroups, missing data, safety, tolerability/persistence), place it in a cross-trial comparison lattice vs SoC and class peers, and size the stock reaction with historical grounding. The judgment core for binary biotech events."
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - clinical-trials
  - readouts
  - cross-trial
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Readout window default 4 quarters; up to 8 for multi-trial programs."
allowed_tools:
  - search_clinical_trials
  - get_clinical_trial
  - search_documents
  - search_sec_filings
  - read_source_outline
  - read_source_pages
  - get_company_profile
  - search_fda_approvals
  - search_investment_cases
  - get_investment_case
  - search_investment_strategies
  - get_investment_strategy
  - search_by_analogue
  - search_knowledge_entries
  - get_knowledge_entry
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught clinical-trial frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| scrutiny_axes | all six + tolerability | Safety/stats/subgroups/missing data/endpoints/benefit-risk + tolerability/persistence as co-equal axis |
| lattice_comparators | SoC + class peers | Every readout is placed against standard of care and same-class peers |
| safety_imbalance | defer to outcomes | Small-N safety imbalances defer the verdict to a larger outcomes trial |
| conflict_policy | materiality-rated | Conflicting readings surfaced verbatim, rated by materiality or deferred |
| outcome_framing | base/bull/bear | Binary readouts need scenario sizing |
| reaction_context | historical cases | Size moves from past analogues |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Triggers

- "Evaluate [ticker]'s upcoming trial readout."
- "What should I look for in [trial]'s data?"
- "Size the readout for [drug] phase 3."
- "What did the AdCom-style scrutiny say about similar trials?"
- "Base/bull/bear for [ticker]'s readout."
- "Which endpoints matter for [trial]?"
- "How has the market reacted to similar readouts?"
- "Readout checklist for [ticker]."
- "Is this trial design adequate?"
- "What are the red flags in [trial]'s design?"

## Production Grounding

- Readout ≠ approval: phase-3 success is necessary but not sufficient; FDA re-analyzes sponsor data.
- Apply the six scrutiny axes (safety signals, statistical adequacy, subgroup analyses, missing data, endpoint appropriateness, benefit-risk) plus tolerability/persistence as a co-equal axis — discontinuation rates, dose reductions, and AE-driven dropout often decide commercial uptake. The 道/法 frameworks in `references/knowledge-frameworks.md` are the authoritative checklist.
- Cross-trial lattice: every readout is placed against standard of care and same-class peers on aligned endpoints; a readout judged in isolation is incomplete.
- Safety-imbalance deferral: a safety imbalance seen at readout scale defers the verdict to a larger outcomes trial; never over-weight small-N imbalances.
- Materiality-rated conflicts: conflicting characterizations of the same data are surfaced verbatim and rated by materiality or deferred — never averaged.
- Readout framing: readout design, then stock sizing (binary-risk expected value), then historical analogue comparison.

## Data Source Priority

1. `search_clinical_trials` / `get_clinical_trial` — design, status, endpoints, dates.
2. `search_documents` / `read_source_*` — sponsor disclosure, prior data cuts.
3. `search_fda_approvals` — regulatory history of the drug/program.
4. Knowledge layer: `search_investment_cases(event_type=trial_readout|adcom_vote)` + strategies for judgment frameworks.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Pull the trial record (`get_clinical_trial` by NCT id, or `search_clinical_trials` by drug/ticker).
2. Assess design + endpoint quality against scrutiny axes, including tolerability/persistence.
3. Build the cross-trial lattice: comparator trials for SoC and class peers on aligned endpoints.
4. Frame base/bull/bear outcomes with sizing; defer safety-imbalance verdicts to outcomes trials where needed.
5. Ground in historical readout/adcom cases via knowledge tools.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Trial record
2. Scrutiny-axes assessment (incl. tolerability/persistence)
3. Cross-trial lattice vs SoC and class peers
4. Outcome scenarios + sizing
5. Analogue grounding

## Modes

- **Pre-readout** (default): design scrutiny + scenario sizing.
- **Post-readout**: results evaluation + reaction context.
- **Program view**: multiple trials across a program.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| search_clinical_trials empty | Use filings + press via `search_documents`; annotate coverage_gap |
| Trial record thin | Note undisclosed fields; do not fabricate |
| Knowledge tools empty | Proceed with structured data + static frameworks |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_trial-readout-analysis_{affix}.md`

## Output Structure

1. **Executive Summary** — readout stance in 2-3 sentences
2. **Trial Profile** — design, endpoints, status, dates
3. **Scrutiny Assessment** — the six axes plus tolerability/persistence, with evidence
4. **Cross-Trial Lattice** — aligned endpoints vs standard of care and class peers
5. **Outcome Scenarios** — base/bull/bear with sizing; safety-imbalance deferrals flagged
6. **Historical Analogues** — cases with /v/ citations
7. **Coverage Gaps** — degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| NCT id unknown | Search by drug/ticker; flag if unresolved |
| Endpoints undisclosed | Flag explicitly; scrutiny limited to disclosed data |
| Conflicting readings of the same data | Surface both verbatim; rate materiality or defer to a larger outcomes trial — never average |
| No comparator data for the lattice | Mark lattice cells unavailable; flag the gap — do not guess |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `references/knowledge-frameworks.md`
