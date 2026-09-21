# risk — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

**Sections** (this skill's own declared elements; each maps to the modes in
`references/modes.md`, which carry the per-mode focus and tool list):

1. **Executive Summary** (≤200 words) — headline conclusions for this dimension
2. **General Risk Factors Identification Assessment** (mode: general-risk-factors-identification-assessment)
3. **Technology Disruption Risk Analysis** (mode: technology-disruption-risk-analysis)
4. **Regulatory Compliance Risk Assessment** (mode: regulatory-compliance-risk-assessment)
5. **External Shock Macro Risk Evaluation** (mode: external-shock-macro-risk-evaluation)
6. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format


The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_risk_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `risk-matrix`, `regulatory-exposure`, `tech-disruption`, `macro-sensitivity`). Examples:

- `LLY/2026-05-25_1430_risk_risk-matrix.md`
- `NVDA/2026-05-25_1545_risk_tech-disruption.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
