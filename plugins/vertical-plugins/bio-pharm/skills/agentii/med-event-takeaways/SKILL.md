---
name: med-event-takeaways
description: Post-event analyst note (conferences, KOL events, site visits) with the professional note anatomy — headline verdict, per-stock takeaways with model numbers, KOL distillation, cross-trial comparison lattices, modeled deltas vs consensus (peak × POS), three what's-changed vectors, risk bullets, and materiality-rated conflicting views. Use after any med event to convert the event into actionable takeaways.
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Event-note window default 4 quarters; up to 8 for multi-trial programs."
allowed_tools:
  - search_documents
  - search_sec_filings
  - list_sources
  - read_source_outline
  - read_source_pages
  - search_investment_cases
  - get_investment_case
  - search_investment_strategies
  - search_by_analogue
  - search_knowledge_entries
  - search_clinical_trials
  - get_clinical_trial
  - search_earnings_calendar
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught sell-side note-writing practice; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| note_anatomy | 9 sections | headline → per-stock → KOL → lattices → deltas → vectors → risks → trackers |
| delta_framing | peak × POS | Modeled deltas vs consensus are unadjusted peak × POS |
| conflict_policy | materiality-rated | Surface verbatim, rate materiality, or defer to an outcomes trial |
| vector_set | estimates/thesis/positioning | The three what's-changed vectors per covered name |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before event queries.

## Triggers

- "Write the note on [conference / KOL event]."
- "What are the takeaways from [event] for my coverage?"
- "Distill the [conference] KOL panel on [drug/class]."
- "What changed for [ticker] after [event]?"
- "Model the delta to consensus from [event]'s data."
- "Which stocks move on [event] and why?"
- "Conflict check: what did KOLs disagree on at [event]?"
- "What do I update first — estimates, thesis, or positioning?"
- "Summarize the cross-trial comparisons from [event]."
- "Upside and downside risks after [event]."
- "Link the living trackers that [event] should update."

## Production Grounding

- Note anatomy is fixed: headline verdict (paragraph one) → per-stock takeaways with model numbers → KOL distillation → raw data + cross-trial lattices → modeled deltas vs consensus (unadjusted peak × POS) → three what's-changed vectors (estimates / thesis / positioning) → risk bullets → living-tracker links.
- Conflict rule: conflicting views surfaced verbatim, rated by materiality ("incremental positive, not narrative-changing") or deferred to a larger outcomes trial — never silently averaged.
- Consensus delta: model-vs-consensus always explicit; POS changes logged with reasons; abstain where unquantifiable.
- Buy-side lens: client-question section, where investor attention sits, per-name bull/bear pivot conditions.
- Badges: `[FACT]`/`[DEDUCTED]`/`[VIEW]` with the summary table.

## Data Source Priority

1. Event content: transcripts/slides via `search_documents` + `list_sources` + `read_source_outline` / `read_source_pages`.
2. Trial context: `search_clinical_trials` / `get_clinical_trial` for the studies discussed.
3. Consensus: `search_earnings_calendar` (company-level); product consensus derived and labeled [DEDUCTED].
4. Knowledge: `search_investment_cases` / `search_investment_strategies` / `search_by_analogue` (sectors=med) for pattern grounding and /v/ citations.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Enumerate the event's covered names, sessions, and data presentations.
2. Retrieve transcripts/abstracts; extract per-presentation data with sources.
3. Pull each discussed trial's record for lattice construction (vs SoC and class peers).
4. Model deltas: unadjusted peak × POS per asset vs consensus, assumptions stated.
5. Ground patterns via `search_investment_cases` / `search_by_analogue` (sectors=med); cite /v/.

### Temporal Scope
See frontmatter temporal_scope block. Notes cover the meeting window plus the forward quarters its data affects.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Event inventory
2. Data extraction (raw numbers + sources)
3. KOL distillation + conflict capture (verbatim)
4. Cross-trial lattices
5. Model deltas vs consensus
6. What's-changed vectors + risk bullets + tracker links

## Modes

- **Conference note** (default): multi-day meeting, per-session distillation.
- **KOL / site visit**: single-source distillation with conflict emphasis.
- **Single-name note**: one covered name with deeper model treatment.
- **Basket**: multi-ticker note with per-name sections.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| Event transcript unavailable | Degrade to abstracts/slides; annotate coverage_gap |
| No consensus figure | State required inputs; label the delta [VIEW] — never fabricate |
| Trial record missing | Lattice cell marked unavailable; do not guess |
| Knowledge tools empty | Event data only; annotate knowledge coverage_gap |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_med-event-takeaways_{affix}.md` (multi-name: `watchlist/{YYYY-MM-DD_HHMM}_med-event-note_{affix}.md`)

## Output Structure

1. **Headline Verdict** — the event in 2-3 sentences
2. **Per-Stock Takeaways** — 2-4 lines each, ≥1 model number
3. **KOL Distillation** — themes + conflicting views verbatim with materiality ratings
4. **Cross-Trial Lattices** — vs standard of care and class peers
5. **Model Deltas vs Consensus** — peak × POS arithmetic, [DEDUCTED] labels
6. **What's Changed** — estimates / thesis / positioning per name
7. **Risk Bullets** — upside and downside
8. **Living-Tracker Links** — trackers to append, never rewrite

## Error Handling

| Error | Fallback |
|-------|----------|
| Conflicting KOL views | Surface both verbatim; rate materiality or defer to an outcomes trial — never average |
| Consensus absent | coverage_gap with required inputs; keep the internal model consistent |
| Event scope unclear | Narrow to named sessions/presentations; flag what is out of scope |

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
