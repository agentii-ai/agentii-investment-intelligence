# agentii.md Memory Index Schema

> **⚠️ RETAINED — NOT SUPERSEDED BY SPEC 046 (T171, Q141/Q144).** This contract is part
> of the **early instrument set** (`agentii.md` + `style.md` + `snapshots/` + `sessions/`,
> defined by three published contracts). 046 does **not** deprecate, delete, or override it.
>
> **"Replaced by `artifacts/`" happens ONLY in thesis mode.** In **single-skill mode** —
> a user invoking one skill against agentii.ai data without creating a thesis — these
> instruments keep exactly their original behaviour, because in that mode there is no
> `artifacts/` to replace them with and no thesis ID to key anything on.
>
> **Measured scale, so this is not a marginal configuration**: **52** skill files reference
> `agentii.md` and **32** reference `sessions/`. Deleting or overriding these contracts
> would break a fifth of the corpus.
>
> **Why this note exists at all**: 046 briefly re-keyed `snapshots/` unconditionally
> (revoked by Q144) and declared rotation rules that assumed every workspace has a
> `constitution.md` (corrected by Q140). Both errors had one shape — **a rule written
> without its premise** — and both would have landed on files that are live in a mode
> neither of the two measured workspaces exercises. A note stating the retention is
> cheaper than rediscovering it.


`agentii.md` at the workspace root is the canonical project memory index. Skills append structured YAML frontmatter blocks after each analysis run. The agent auto-reads `agentii.md` on session start per the workspace VM provisioning sequence .

## Two roles — WHICH ONE DEPENDS ON `constitution.md` (Q140, T159)

`agentii.md` is **one file with two roles**, and the file that decides which one is
`constitution.md` — not the content of `agentii.md` itself:

| `constitution.md` | role of `agentii.md` | consequences |
|---|---|---|
| **present** | **chronicle** — the memory index this contract describes | append-only; Q81's per-period rotation applies normally |
| **absent** | **it IS the constitution** | it bears the project's principles; **Q81 rules 1–2 do NOT apply** — rotating it would rotate away the constitution |

Detection is one filesystem read, workspace-scoped, no new state:
`agentii_cmd.detect_instrument(workspace)`. It is **not** the same predicate as mode
detection, which is run-scoped (Q143) — a workspace can be constitution-governed *and*
running a standalone skill.

**Why this is written here rather than assumed.** Q81's rotation and Q83's prohibition
both assumed every workspace has a `constitution.md`. They do not. Where there is none,
`agentii.md` is the constitution, and a rotation justified by that false premise
**executes a destructive action** — this spec's seventh instance of one recurring defect
and the first that destroys rather than merely mis-reporting. A wrong number is corrected
by the next check; a rotated constitution is gone.

`python3 scripts/reconcile_instruments.py --workspace <dir>` reports which role a
workspace is in, whether rotation is safe, and — for a workspace already migrated — which
principles the new `constitution.md` did not carry over. Migration is one-way, so that
reconciler is the only thing that can catch a drop nobody decided.

## YAML Block Format

Skills MUST append the following block after writing their output file:

```yaml
---
ticker: LLY
date: 2026-06-03
skill: recent-quarter
output_file: LLY/2026-06-03_1430_recent-quarter_consolidated-p-and-l.md
key_conclusions: Q1 2026 revenue $18.5B (+12% QoQ), EPS $2.34 beat consensus by 4%, gross margin expanded 200bps to 80%. Mounjaro supply constraints easing.
snapshot_ref: snapshots/LLY/2026-06-03_thesis.md # optional, present only if snapshot synthesized
---
```

## Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ticker` | Yes | string | Uppercase ticker symbol (or `tickers: [...]` for multi-ticker per FR-106) |
| `date` | Yes | ISO 8601 | Date of analysis run |
| `skill` | Yes | string | Skill name matching YAML frontmatter `name` field |
| `output_file` | Yes | relative path | Path to the per-skill output file from workspace root |
| `key_conclusions` | Yes | string | 1-3 sentence synthesis of key findings |
| `snapshot_ref` | No | relative path | Path to latest snapshot if one was synthesized  |

## Append Convention

- Skills MUST append entries — NEVER delete or modify existing entries.
- If `agentii.md` does not exist, create it with a `# Project Memory Index` heading before the first entry.
- Entries are appended at end of file, separated by `---` if prior entries exist.
- Chronological order is maintained naturally by append-only pattern.

## Auto-Discovery Protocol

On session start, the agent MUST:

1. Read `agentii.md` if it exists.
2. Parse all YAML frontmatter blocks to build an in-memory index.
3. For the requested ticker, extract all entries where `ticker` matches (or `tickers` array contains the ticker per FR-106).
4. Build a concise memory summary: prior skills run, latest key conclusions, available output files and snapshots.
5. Inject this summary into context BEFORE executing any data retrieval ( pre-flight).

## Cross-Reference

- ****: Per-skill output file convention
- ****: YAML frontmatter in output files
- ****: Two-tier output model (raw analysis + snapshots)
- ****: Multi-ticker output convention (`tickers: [...]` array)
- ****: Session archival (`sessions/INDEX.md` for session index)
