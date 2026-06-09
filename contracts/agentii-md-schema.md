# agentii.md Memory Index Schema

`agentii.md` at the workspace root is the canonical project memory index. Skills append structured YAML frontmatter blocks after each analysis run. The agent auto-reads `agentii.md` on session start per the workspace VM provisioning sequence .

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
