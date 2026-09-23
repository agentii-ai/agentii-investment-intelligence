---
name: pipeline-medicines
description: "Medicines pipeline analysis over structured universes: Phase I-III assets with probability-of-success discipline (unadjusted peak x POS = modeled value; POS changes logged with reasons), trial status-diff tracking, and mechanism/competitor mapping via drug-knowledge lookups."
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 8
  max_quarters: 20
  description: "Long-horizon pipeline window default 8 quarters; up to 20 for multi-year development programs."
allowed_tools:
  - get_company_drugs
  - search_universe_drugs
  - search_drug_knowledge
  - get_drug_knowledge
  - search_drugs_by_target
  - search_drugs_by_indication
  - search_clinical_trials
  - get_clinical_trial
  - search_fda_approvals
  - search_companies
  - get_company_profile
  - search_earnings_calendar
  - search_investment_cases
  - search_knowledge_entries
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught pipeline-valuation frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| asset_scope | all disclosed assets | Full-pipeline enumeration first |
| pos_source | published phase transition ranges | Starting point, then adjusted with logged reasons |
| status_diff | true | Previous vs current trial status shown per asset |
| competitor_map | true | Same-target and same-indication crowding surfaced |
| value_frame | risk-adjusted | Modeled value = unadjusted peak x POS, both shown |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md` — carry the `_run_id` from your first tool result and name yourself (and your parent, if you were spawned). Confirm ticker resolution via `search_companies` before asset queries.

## Triggers

- "Analyze [ticker]'s drug pipeline by phase."
- "What are the Phase II and III assets for [ticker]?"
- "Risk-adjust [ticker]'s pipeline with explicit POS assumptions."
- "Which of [ticker]'s programs is most valuable?"
- "What trials recently changed status for [ticker]?"
- "Who else is targeting [mechanism/target]?"
- "How crowded is [indication], and what does that mean for [ticker]?"
- "Log every POS change with reasons for [ticker]'s pipeline."
- "What is the next catalyst for each of [ticker]'s assets?"
- "Compare [ticker]'s pipeline against same-indication competitors."
- "Map [ticker]'s assets by mechanism of action."
- "What does [ticker]'s pipeline say about its runway?"

## Production Grounding

- POS discipline: every asset carries an unadjusted peak sales estimate and a phase-appropriate POS; the modeled number is peak x POS, never a bare risk-adjusted figure. Every POS change is logged with its reason (trial data, competitor data, discontinuation) — silent POS drift is a defect.
- Phase ladder: Phase I safety/dosing, Phase II efficacy signal, Phase III registrational; option value rises with phase. Apply scrutiny axes when sizing pivotal assets.
- Status-diff discipline: show previous vs current status per trial (New/Suspended/Terminated/Ahead/Delayed/...); Terminated plus enrollment collapse is a red flag; recruitment-complete starts the readout clock.
- Competitor mapping: same-target and same-indication crowding discounts peak sales, not just POS; mechanism overlap explains class risk.
- Grounding detail lives in `references/knowledge-frameworks.md`.

## Data Source Priority

1. `get_company_drugs` / `search_universe_drugs` — asset inventory from the med universe.
2. `search_drug_knowledge` / `get_drug_knowledge` — mechanism, targets, indications, phase per drug.
3. `search_drugs_by_target` / `search_drugs_by_indication` — reverse lookups for the competitor map.
4. `search_clinical_trials` / `get_clinical_trial` — status, enrollment, primary-completion dates.
5. `search_fda_approvals` — registration history; `search_earnings_calendar` for timing; knowledge layer via `search_investment_cases` / `search_knowledge_entries`.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Pull asset inventory (`get_company_drugs`), then universe cross-checks (`search_universe_drugs`).
2. Enrich per asset from `search_drug_knowledge` / `get_drug_knowledge` (mechanism, targets, phase).
3. Pull trial records (`search_clinical_trials`) for status-diff and next-catalyst dates.
4. Build the competitor map via `search_drugs_by_target` / `search_drugs_by_indication`.
5. Size each asset (peak x POS with change log); ground in cases and knowledge entries.

### Temporal Scope
See frontmatter temporal_scope block. Development programs span years; status history may reach back 8-12 quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Asset enumeration
2. Phase and mechanism enrichment
3. Status-diff and catalyst dating
4. Competitor map assembly
5. POS model with change log

## Modes

- **Phase scan** (default): all assets by phase with status-diff and next catalyst.
- **POS model**: peak x POS modeling with a full change log and scenario brackets.
- **Competitor map**: target/indication crowding with class-risk read.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_company_drugs empty | `search_universe_drugs` by company or indication; annotate coverage_gap |
| Drug-knowledge record missing | Flag mechanism/competitor data unavailable; never infer targets |
| No trial rows | Mark status undisclosed; note the readout clock is unverified |
| Knowledge tools empty | Proceed with structured data only |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_pipeline-medicines_{affix}.md`

## Output Structure

1. **Executive Summary** — pipeline stance in 2-3 sentences
2. **Asset Table** — phase, indication, mechanism, status-diff, next catalyst
3. **POS Model** — unadjusted peak, POS, modeled value per asset, change log with reasons
4. **Competitor Map** — same-target and same-indication crowding, class risk
5. **Historical Context** — cases and knowledge entries with /v/ citations
6. **Coverage Gaps** — missing records, undisclosed status, degraded modes

## Error Handling

| Error | Fallback |
|-------|----------|
| Phase unknown | Mark "undisclosed"; do not guess |
| POS source missing | State the assumption range and label it a judgment |
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
