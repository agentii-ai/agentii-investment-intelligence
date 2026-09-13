---
name: pipeline-vaccines
description: "Vaccine pipeline analysis: immunogenicity and seroconversion studies, lot-consistency trials, healthy-population efficacy designs, and age-cohort bridging, with the ACIP gate built into the value path across the med universe."
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "Long-horizon pipeline window default 8 quarters; up to 20 for multi-season bridging and booster cycles."
allowed_tools:
  - get_company_drugs
  - search_universe_drugs
  - search_acip_events
  - get_acip_event
  - search_clinical_trials
  - get_clinical_trial
  - search_fda_approvals
  - search_companies
  - search_knowledge_entries
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught vaccine development frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| asset_scope | all disclosed vaccine assets | Full-pipeline enumeration first |
| evidence_lens | immunogenicity + efficacy | Correlate studies distinguished from efficacy trials |
| acip_gate | true | ACIP path modeled as part of pipeline value |
| cohort_lens | true | Age-cohort bridging tracked per asset |
| value_frame | risk-adjusted | Modeled value = unadjusted peak x POS, both shown |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before asset queries.

## Triggers

- "Analyze [ticker]'s vaccine pipeline."
- "What seroconversion or immunogenicity studies support [vaccine]?"
- "Where are [ticker]'s vaccines in the efficacy ladder?"
- "Which lot-consistency trials are pending for [ticker]?"
- "What age-cohort bridging studies does [ticker] have planned?"
- "Does [ticker]'s vaccine have an ACIP path?"
- "Risk-adjust [ticker]'s vaccine pipeline."
- "What is the next catalyst for each of [ticker]'s vaccine assets?"
- "How do healthy-population efficacy designs change the evidence bar?"
- "Map [ticker]'s vaccines by antigen, cohort, and phase."
- "Which vaccine assets could reach a BLA in the next two years?"
- "What does [ticker]'s pipeline say about its seasonal strategy?"

## Production Grounding

- Vaccine evidence ladder: immunogenicity/seroconversion studies (correlates, not efficacy) → efficacy trials in healthy populations (large N, safety-first) → lot-consistency trials (immunogenicity equivalence across three manufacturing lots — a licensure gate) → age-cohort bridging for pediatric and elderly label expansion.
- Healthy-population design: the efficacy bar is safety-first; endpoints prevent infection or disease; power comes from large N, and placebo arms shrink post-licensure (non-inferiority and bridging designs follow).
- Lot consistency is a regulatory milestone, not a formality: without it, licensure stalls regardless of efficacy data.
- The ACIP gate is part of pipeline value: a Phase III vaccine without a plausible ACIP path carries an unmodeled commercial step.
- Booster cycles and variant updates re-open the market; cohort bridging extends the label beyond the pivotal population.
- Grounding detail lives in `references/knowledge-frameworks.md`.

## Data Source Priority

1. `get_company_drugs` / `search_universe_drugs` — vaccine asset inventory.
2. `search_clinical_trials` / `get_clinical_trial` — study design type, cohorts, status-diff, enrollment.
3. `search_acip_events` / `get_acip_event` — the gate path per vaccine; `search_fda_approvals` for BLA history.
4. Knowledge layer: `search_knowledge_entries` for framework grounding.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Pull vaccine assets (`get_company_drugs`), cross-check the universe (`search_universe_drugs`).
2. Enrich per asset with trial records (`search_clinical_trials`) — design type, cohorts, status.
3. Map the ACIP path per asset (`search_acip_events` / `get_acip_event`).
4. Layer BLA and approval history (`search_fda_approvals`).
5. Size each asset (peak x POS); ground in knowledge entries.

### Temporal Scope
See frontmatter temporal_scope block. Seasonal and bridging cycles span years; history may reach back 8-12 quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Asset enumeration
2. Evidence-ladder mapping (immunogenicity → efficacy → lot consistency → bridging)
3. ACIP-path assessment
4. Cohort and booster overlay
5. Risk-adjusted synthesis

## Modes

- **Phase scan** (default): all vaccine assets by stage with next catalyst and ACIP path.
- **Cohort bridge**: age-cohort expansions, booster cycles, and label breadth.
- **Competitor map**: antigen and indication overlap with class-read.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_drugs empty | `search_universe_drugs` by company or indication; annotate coverage_gap |
| No trial rows | Mark design type undisclosed; do not guess efficacy vs immunogenicity |
| No ACIP rows | Flag the gate path unmodeled; never assume approval = availability |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_pipeline-vaccines_{affix}.md`

## Output Structure

1. **Executive Summary** — pipeline stance in 2-3 sentences
2. **Asset Table** — stage, design type, cohorts, next catalyst, ACIP path
3. **Evidence Ladder** — immunogenicity vs efficacy vs lot-consistency status per asset
4. **Cohort & Booster Map** — bridging studies, label breadth, seasonal strategy
5. **Risk-Adjusted Sizing** — peak x POS with the two-gate path made explicit
6. **Coverage Gaps** — missing records, undisclosed design, degraded modes

## Error Handling

| Error | Fallback |
|-------|----------|
| Study design unknown | Mark "undisclosed"; do not guess |
| Efficacy vs correlate ambiguity | State both readings; never call seroconversion efficacy |
| No catalysts found | Say so explicitly; note the pipeline may be early-stage |

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
