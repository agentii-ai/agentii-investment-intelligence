# turnaround — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

**Sections** (this skill's own declared elements; each maps to the modes in
`references/modes.md`, which carry the per-mode focus and tool list):

1. **Executive Summary** (≤200 words) — headline conclusions for this dimension
2. **Performance Stagnation Detection and Classification** (mode: performance-stagnation-detection-and-classification)
3. **Growth Catalyst Identification and Assessment** (mode: growth-catalyst-identification-and-assessment)
4. **Growth Catalyst Execution Monitoring and Progress Assessment** (mode: growth-catalyst-execution-monitoring-and-progress-assessment)
5. **Leadership Change Impact Analysis** (mode: leadership-change-impact-analysis)
6. **Strategic Leadership Impact Assessment and Financial Projection** (mode: strategic-leadership-impact-assessment-and-financial-projection)
7. **Strategic Initiative Execution Status and Effectiveness Assessment** (mode: strategic-initiative-execution-status-and-effectiveness-assessment)
8. **Operational Execution Progress and Effectiveness Assessment** (mode: operational-execution-progress-and-effectiveness-assessment)
9. **New Product Performance Evaluation and Turnaround Contribution Assessment** (mode: new-product-performance-evaluation-and-turnaround-contribution-assessment)
10. **Financial Turnaround Metrics and Performance Validation** (mode: financial-turnaround-metrics-and-performance-validation)
11. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format


The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_turnaround_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `turnaround-thesis`, `restructuring-progress`, `cost-action`, `inflection-signals`). Examples:

- `LLY/2026-05-25_1430_turnaround_turnaround-thesis.md`
- `NVDA/2026-05-25_1545_turnaround_restructuring-progress.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
