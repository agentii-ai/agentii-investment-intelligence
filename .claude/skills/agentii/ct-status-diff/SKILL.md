---
name: ct-status-diff
description: "Weekly clinical-trial status diff — the 11-category change report over the stored weekly snapshots (spec 055 FR-B03). Surfaces exactly what changed on the trial registry for your coverage: New / Suspended / Withdrawn / Terminated / Recruiting / Recruitment-Complete / Completed / Ahead / Delayed / Upsized / Downsized, every row carrying previous and new values, with risk flags on Terminated and Downsized and re-timing flags on Ahead and Delayed. The stored-previous-value discipline makes each week's diff reproducible."
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Weekly diff over the latest two snapshots by default; up to 8 quarters of diff history on request."
allowed_tools:
  - get_ct_status_changes
  - search_clinical_trials
  - get_clinical_trial
  - search_companies
  - get_company_profile
  - search_investment_cases
  - search_by_analogue
  - search_knowledge_entries
  - get_knowledge_entry
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught clinical-trial monitoring frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| window | latest two snapshots | The diff is always between consecutive stored states |
| categories | all 11 | Complete change report; filter on request |
| risk_flags | on | Terminated / Downsized are surfaced first |
| gap_statement | on | Missing snapshot weeks are stated, never inferred |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm the snapshot coverage via `get_ct_status_changes` before framing any readout.

## Triggers

- "What changed on clinicaltrials.gov for my coverage this week?"
- "Which of [ticker]'s trials moved this week?"
- "Any trial delays or accelerations in my watchlist?"
- "Flag every terminated or downsized trial since last week."
- "Did any recruitment complete for [ticker]?"
- "Show the previous and new primary-completion dates for [drug]'s program."
- "Which trials were upsized this week?"
- "Is [trial]'s enrollment collapsing?"
- "Summarize the week's trial-registry changes for the sector."
- "What should I re-check ahead of [readout] based on registry moves?"
- "Compare this week's diff to the month-ago diff."

## Production Grounding

- The diff is a stored-state comparison: every row pairs a NEW value with the PREVIOUS value from the prior snapshot — the previous-value column is the discipline; a row without both is a defect.
- The 11-category taxonomy: New / Suspended / Withdrawn / Terminated / Recruiting / Recruitment-Complete / Completed / Ahead / Delayed / Upsized / Downsized.
- Risk signals: Terminated and Downsized (enrollment collapse is the earliest visible distress). Re-timing alerts: Ahead / Delayed primary-completion moves.
- Recruitment-Complete means the readout clock has started — treat it as a catalyst-date confirmation.
- Gap windows: if snapshots are not consecutive archive writes, the gap is stated on the rows — a change is never attributed across a missing week.
- Determinism: identical snapshots yield byte-identical diffs; never invent an intermediate state.
- Badge discipline: `[FACT]` registry rows, `[DEDUCTED]` interpretations, `[VIEW]` positioning, with the summary table.

## Data Source Priority

1. `get_ct_status_changes` — the stored-weekly-snapshot diff (pipeline.ct_status_snapshot).
2. Trial context: `search_clinical_trials` / `get_clinical_trial` for design and endpoints.
3. Company context: `search_companies` / `get_company_profile`.
4. Historical grounding: `search_investment_cases` (event_type=termination/delay/safety) + `search_by_analogue`.
5. Knowledge: `search_knowledge_entries` for trial-judgment patterns.

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
1. Pull the weekly diff via `get_ct_status_changes` (ticker-filtered for single names, sector-wide for watchlists).
2. Rank rows: risk signals first, then re-timing, then recruiting/completed, then new.
3. For each risk-signal row, pull the trial's design via `get_clinical_trial` and state what changed and what it implies.
4. Ground termination/delay reads in `search_investment_cases` / `search_by_analogue` (sectors=med); cite /v/ records.
5. Attach the gap-window statement verbatim wherever the tool reports one.

### Temporal Scope
See frontmatter temporal_scope block. Historical diff series (month-over-month) available on request.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Snapshot-diff pull
2. Risk/re-timing triage
3. Per-signal trial context
4. Historical grounding
5. Weekly change report + watch flags

## Modes

- **Watchlist** (default): one diff report across the basket, sorted risk-first.
- **Single ticker**: per-trial change ledger with trial context.
- **Signal scan**: restrict to risk signals (Terminated/Downsized) or re-timing (Ahead/Delayed).

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_ct_status_changes empty (<2 snapshots) | State the coverage gap: the diff needs two consecutive snapshot cycles; use search_clinical_trials metadata as a degraded view |
| Trial not in snapshots | Flag as registry-coverage gap; do not fabricate a previous value |
| Knowledge tools empty | Proceed with structured diff only; annotate knowledge coverage_gap |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_ct-status-diff_{affix}.md` (watchlist: `watchlist/{YYYY-MM-DD_HHMM}_ct-status-diff_{affix}.md`)

## Output Structure

1. **Executive Summary** — the week in trial-registry changes, 2-3 sentences
2. **Risk Signals** — Terminated / Downsized rows with previous/new values and trial context
3. **Re-Timing Alerts** — Ahead / Delayed rows with date deltas
4. **Flow Changes** — New / Recruiting / Recruitment-Complete / Completed / Suspended / Withdrawn rows
5. **Gap Statement** — snapshot windows with missing weeks stated
6. **Watch Flags** — what to re-check before the next readout
7. **Coverage Gaps** — missing snapshots, unregistered trials, degraded modes

## Error Handling

| Error | Fallback |
|-------|----------|
| Fewer than 2 snapshots | coverage_gap with the two-cycle requirement; degraded metadata view only |
| Empty diff | State it plainly — a clean week is a valid result; never pad |
| Ticker not in med universe | Resolve via company match; surface the classification gap |

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
