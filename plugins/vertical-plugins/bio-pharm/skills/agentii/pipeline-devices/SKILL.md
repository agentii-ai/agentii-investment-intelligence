---
name: pipeline-devices
description: "Device pipeline analysis: feasibility and pivotal study stages, design-iteration cycles, RWE studies, and post-market obligations, with reimbursement-aware value framing and decision-track awareness across the med universe."
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - pipeline
  - device-pathways
  - rwe
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "Long-horizon pipeline window default 8 quarters; up to 20 for multi-year device development and post-market programs."
allowed_tools:
  - get_company_devices
  - search_universe_devices
  - search_clinical_trials
  - get_clinical_trial
  - get_device_decision
  - search_companies
  - get_company_profile
  - search_knowledge_entries
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught medtech pipeline frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| asset_scope | all disclosed devices | Full-pipeline enumeration first |
| stage_lens | feasibility + pivotal | Design-iteration stages, not drug-phase labels |
| reimbursement_aware | true | Value framed against coverage paths, not raw approval |
| post_market_scan | true | Obligations and surveillance state surfaced |
| value_frame | risk-adjusted | Modeled value = unadjusted peak x POS, both shown |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before asset queries.

## Triggers

- "Analyze [ticker]'s device pipeline."
- "What is in [ticker]'s feasibility and pivotal portfolio?"
- "Where is each of [ticker]'s devices in its design cycle?"
- "Which of [ticker]'s programs are approaching submission?"
- "What RWE studies support [ticker]'s devices?"
- "What post-market obligations does [ticker] carry?"
- "Risk-adjust [ticker]'s device pipeline."
- "What is the next catalyst for each of [ticker]'s devices?"
- "How does [ticker]'s device pipeline compare to peers?"
- "Which device classifications (PMA/De Novo/510(k)) map to [ticker]'s pipeline?"
- "Map [ticker]'s devices by clinical stage and indication."
- "What does [ticker]'s pipeline say about its reimbursement path?"

## Production Grounding

- Device stage ladder: feasibility (first-in-human, small N) → pivotal (registrational) → submission (PMA / De Novo / 510(k)) → post-market. Devices iterate through design versions; design freezes and iteration cycles are the pipeline milestones, not drug-style phases.
- Pivotal design varies by classification: PMA demands the highest evidence bar, De Novo novel classification, 510(k) equivalence — the pipeline's value path depends on the expected track.
- RWE studies (registries, claims analyses) increasingly support coverage and label expansion; treat them as pipeline assets with their own timelines.
- Post-market obligations (surveillance studies, MDR reporting) shape long-term liability and the re-approval path.
- Reimbursement-aware framing: pipeline value assumes a coverage path; an asset without one is discounted.
- Grounding detail lives in `references/knowledge-frameworks.md`.

## Data Source Priority

1. `get_company_devices` / `search_universe_devices` — asset inventory from the med universe.
2. `search_clinical_trials` / `get_clinical_trial` — study stage, design type, status, enrollment.
3. `get_device_decision` — decision history and upcoming decisions per device.
4. Knowledge layer: `search_knowledge_entries` for framework grounding.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Pull asset inventory (`get_company_devices`), cross-check the universe (`search_universe_devices`).
2. Enrich per asset with study records (`search_clinical_trials`) — stage, design type, status-diff.
3. Pull decision history and upcoming dates (`get_device_decision`).
4. Flag post-market obligations and RWE study presence per asset.
5. Size each asset (peak x POS); ground in knowledge entries.

### Temporal Scope
See frontmatter temporal_scope block. Device development and post-market windows span years; history may reach back 8-12 quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Asset enumeration
2. Stage and design-cycle mapping
3. Decision-track alignment
4. Post-market and RWE overlay
5. Risk-adjusted synthesis

## Modes

- **Phase scan** (default): all devices by stage with next catalyst and expected track.
- **Design cycle**: design-iteration state, freezes, and submission readiness.
- **Post-market**: obligations, surveillance state, and RWE support.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_devices empty | `search_universe_devices` by company or indication; annotate coverage_gap |
| No trial rows | Mark stage undisclosed; do not guess pivotal vs feasibility |
| No decision history | Flag the submission track unknown; state both possibilities |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_pipeline-devices_{affix}.md`

## Output Structure

1. **Executive Summary** — pipeline stance in 2-3 sentences
2. **Asset Table** — stage, design type, expected track, next catalyst
3. **Design-Cycle Read** — iteration state, freezes, submission readiness
4. **Post-Market & RWE** — obligations, surveillance, registries
5. **Risk-Adjusted Sizing** — peak x POS with reimbursement framing
6. **Coverage Gaps** — missing records, undisclosed stage, degraded modes

## Error Handling

| Error | Fallback |
|-------|----------|
| Stage unknown | Mark "undisclosed"; do not guess |
| Classification ambiguous | State the evidence-bar difference across tracks |
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
