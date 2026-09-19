# Snapshot Synthesis & Claim Taxonomy (shared include, FR-091 + FR-092)

Canonical two-tier output model and the FACT/DEDUCTED/VIEW claim taxonomy. Skills
reference this file with a one-line `## Snapshot` pointer.

## Two-tier output model (FR-091)

| Tier | Path | Auto-load? | Purpose |
|------|------|-----------|---------|
| Raw analysis | `{ticker}/{YYYY-MM-DD_HHMM}_{skill}_{affix}.md` | No | Full per-run deliverable |
| Snapshot (thesis) | `snapshots/{ticker}/{YYYY-MM-DD}_{semantic-slug}.md` | Yes | Point-in-time investment thesis, restored on session start |

> **⚠️ THIS FILE IS NOT SUPERSEDED BY SPEC 046, AND ITS KEY WAS RIGHT ALL ALONG (T171/T166, 2026-09-18).**
>
> 046 briefly re-keyed `snapshots/` to `{nnn}-{slug}`. **Q144 revoked that**, and this is the record of why:
> `{nnn}-{slug}` exists **only in thesis mode** — in single-skill mode there is no thesis ID, so the key was
> **undefined** in the very mode the contract also serves. The published key `{ticker}/` is valid in both
> modes, because a ticker always exists. **Nothing in this file needed to change**; the narrowing was 046's
> error, not this contract's omission.
>
> **Filename** (Q144): `{YYYY-MM-DD}_{semantic-slug}.md`. The date orders; the slug says what the snapshot is
> about. The previous fixed `_thesis` is a degenerate slug, not a different convention — a snapshot that is not
> about the whole thesis (`_guidance-cut`, `_margin-bridge`) is the case the slug exists for.
>
> **Thesis attribution goes in FRONTMATTER, never in the path.** The one observed instance in the live
> evidence base put it in the path (`snapshots/001-physical-ai-technology-baseline/2026-09-10_thesis.md`,
> `session-history-these001-first-run-0910-1858.md` L157) — which works in thesis mode and has no meaning
> outside it. `ticker` in the path + thesis in frontmatter is the form that holds in both.
>
> **Retained, not deprecated**: `snapshots/` is part of the early instrument set (`agentii.md` + `style.md` +
> `snapshots/` + `sessions/`) that Q141/Q144 keep. "Replaced by `artifacts/`" happens **only in thesis mode**.

After writing the raw deliverable, synthesize/update the ticker's snapshot at
`snapshots/{ticker}/{YYYY-MM-DD}_{semantic-slug}.md`: a concise (≤400 word)
point-in-time thesis that merges this run's conclusions with the prior snapshot.
Note explicitly which prior conclusions are **confirmed**, **updated**, or
**superseded**.

> **This paragraph said `{YYYY-MM-DD}_thesis.md` until 2026-09-19 (T196).** The table
> above had already been corrected by Q144; the instruction had not — so the file
> stated the new filename in its summary and the old one in the line a reader
> actually follows. That is T193's defect class (a corrected rule surviving beside
> its own correction) found one level down, in the file T193's fix pointed at.
> The slug names what the snapshot is *about*: `thesis` when it covers the whole
> thesis, `guidance-cut` / `margin-bridge` when it does not.

## Claim taxonomy (FR-092)

Every material claim in the deliverable MUST carry a **class**, as a structured
field — `claim_class ∈ {FACT, DEDUCTED, VIEW}` on the claim record:

| Class | Meaning | Requirement |
|-------|---------|-------------|
| `FACT` | Directly retrieved from a filing or XBRL fact | MUST carry an inline `/v/` citation |
| `DEDUCTED` | Computed/derived from facts (ratios, growth, mix) | MUST reference the input facts |
| `VIEW` | Analyst interpretation / forward judgment | No citation required; clearly marked as opinion |

- The class is a **field**; the inline `[FACT]` / `[DEDUCTED]` / `[VIEW]` badge is
  **rendering generated from it**, not the source of truth. Where the two disagree,
  the field wins and the disagreement is a defect to report — the same single-source
  discipline Q140/Q141 apply to `agentii.md` and `snapshots/`.
  > **Why a field, and not the badge (Q146/T169).** A G1 gate is defined as
  > deterministic, pure-script, millisecond, zero-LLM. Counting claims by scanning
  > prose for `[FACT]` makes the gate parse writing — so a claim badged slightly
  > differently is silently not counted, and the gate returns a clean result over an
  > input it never read. The badge is for the reader; the field is for the gate.
- Use the rendered badge at the start of the bullet/sentence:
  `[FACT] Q1 revenue was $18.5B [📄 NVDA 10-Q p.4](...)`.
- The summary table near the top of the deliverable carries
  `facts_count` / `deducted_count` / `views_count`. These are **DERIVED** — counted
  from the claims' `claim_class`, never authored independently. Three numbers that
  must agree by construction are three numbers that can disagree silently.

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
