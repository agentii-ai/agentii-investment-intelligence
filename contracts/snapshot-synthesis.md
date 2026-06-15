# Snapshot Synthesis & Claim Taxonomy (shared include, FR-091 + FR-092)

Canonical two-tier output model and the FACT/DEDUCTED/VIEW claim taxonomy. Skills
reference this file with a one-line `## Snapshot` pointer.

## Two-tier output model (FR-091)

| Tier | Path | Auto-load? | Purpose |
|------|------|-----------|---------|
| Raw analysis | `{ticker}/{YYYY-MM-DD_HHMM}_{skill}_{affix}.md` | No | Full per-run deliverable |
| Snapshot (thesis) | `snapshots/{ticker}/{YYYY-MM-DD}_thesis.md` | Yes | Point-in-time investment thesis, restored on session start |

After writing the raw deliverable, synthesize/update the ticker's thesis snapshot
at `snapshots/{ticker}/{YYYY-MM-DD}_thesis.md`: a concise (≤400 word)
point-in-time thesis that merges this run's conclusions with the prior snapshot.
Note explicitly which prior conclusions are **confirmed**, **updated**, or
**superseded**.

## Claim taxonomy (FR-092)

Every material claim in the deliverable MUST be classified with an inline prefix
badge:

| Badge | Meaning | Requirement |
|-------|---------|-------------|
| `[FACT]` | Directly retrieved from a filing or XBRL fact | MUST carry an inline `/v/` citation |
| `[DEDUCTED]` | Computed/derived from facts (ratios, growth, mix) | MUST reference the input facts |
| `[VIEW]` | Analyst interpretation / forward judgment | No citation required; clearly marked as opinion |

- Use the inline prefix at the start of the bullet/sentence:
  `[FACT] Q1 revenue was $18.5B [📄 NVDA 10-Q p.4](...)`.
- Include a small summary table near the top of the deliverable with the counts
  (`facts_count`, `deducted_count`, `views_count`) — these MUST match the output
  frontmatter (`contracts/output-frontmatter-schema.md`).

## Session archival (FR-095)

Archive the run transcript to `sessions/{YYYY-MM-DD}/{HHMM}_{session_id}.jsonl`
and append a one-row entry to `sessions/INDEX.md` (auto-loaded catalog). Raw
session transcripts are NOT auto-loaded — they are read on demand via
`read_session`. See `contracts/session-format.md`.

## Cross-Reference

- `contracts/output-frontmatter-schema.md` — required output frontmatter
- `contracts/memory-load.md` — pre-flight memory load
- `contracts/agentii-md-schema.md` — memory index
- `contracts/session-format.md` — session archival format
