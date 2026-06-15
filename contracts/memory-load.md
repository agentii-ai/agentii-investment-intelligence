# Memory Load Contract (shared include, FR-090)

Canonical pre-flight "Memory Load" step. Skills reference this file with a
one-line `## Memory Load` pointer. Executed during Preflight, BEFORE any data
retrieval, so prior conclusions for the ticker are already in context.

## Sequence

1. **Glob for prior output**: `ls {ticker}/*.md` for single-ticker analyses;
   `ls _cross/*{ticker}*.md` and `ls _sector/*{ticker}*.md` for multi-ticker
   analyses involving this ticker.
2. **Read the memory index**: read `agentii.md` (workspace root) if present and
   parse every YAML frontmatter block (see `contracts/agentii-md-schema.md`).
3. **Parse frontmatter only**: `head -20` each matched output file to extract its
   YAML frontmatter (`key_metrics`, `conclusions`, `facts_count`, …) — do NOT
   load full file bodies.
4. **Load latest snapshot**: if `snapshots/{ticker}/{date}_thesis.md` exists, read
   the most recent one for thesis continuity (see
   `contracts/snapshot-synthesis.md`).
5. **Build memory summary**: aggregate `key_metrics` + `conclusions` across all
   prior analyses for this ticker into a concise summary.
6. **Inject into context**: include the memory summary in the agent's initial
   context BEFORE any tool calls begin. Note which prior conclusions this run will
   confirm, update, or supersede.

This realizes the File-First Hybrid Architecture — machine-parseable metadata
without a vector database.

## Cross-Reference

- `contracts/agentii-md-schema.md` — memory index format
- `contracts/output-frontmatter-schema.md` — per-file frontmatter schema
- `contracts/snapshot-synthesis.md` — two-tier output / snapshot model
- `contracts/session-format.md` — session archival + `sessions/INDEX.md`
