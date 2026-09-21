# growth-strategy — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

**Sections** (this skill's own declared elements; each maps to the modes in
`references/modes.md`, which carry the per-mode focus and tool list):

1. **Executive Summary** (≤200 words) — headline conclusions for this dimension
2. **Growth Strategy Assessment** (mode: growth-strategy-assessment)
3. **Organic Growth Drivers Analysis** (mode: organic-growth-drivers-analysis)
4. **Organic Growth Driver Execution Assessment** (mode: organic-growth-driver-execution-assessment)
5. **Inorganic Growth Drivers Analysis** (mode: inorganic-growth-drivers-analysis)
6. **Inorganic Growth Driver Execution Assessment** (mode: inorganic-growth-driver-execution-assessment)
7. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format


The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_growth-strategy_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `strategy-decomposition`, `capital-allocation`, `m-and-a-pipeline`, `geographic-expansion`). Examples:

- `LLY/2026-05-25_1430_growth-strategy_strategy-decomposition.md`
- `NVDA/2026-05-25_1545_growth-strategy_capital-allocation.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
