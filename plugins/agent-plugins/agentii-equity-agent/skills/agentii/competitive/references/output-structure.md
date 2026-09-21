# competitive — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

**Sections** (this skill's own declared elements; each maps to the modes in
`references/modes.md`, which carry the per-mode focus and tool list):

1. **Executive Summary** (≤200 words) — headline conclusions for this dimension
2. **Direct Competitor Identification and Analysis** (mode: direct-competitor-identification-and-analysis)
3. **Market Share Dynamics Analysis** (mode: market-share-dynamics-analysis)
4. **Market Share Evolution and Competitive Benchmarking** (mode: market-share-evolution-and-competitive-benchmarking)
5. **Forward Looking Market Share Outlook and Strategic Assessment** (mode: forward-looking-market-share-outlook-and-strategic-assessment)
6. **Market Concentration and Competitive Positioning Analysis** (mode: market-concentration-and-competitive-positioning-analysis)
7. **Market Share Growth Drivers and Retention Risk Analysis** (mode: market-share-growth-drivers-and-retention-risk-analysis)
8. **Market Share Capture Efficiency and Execution Analysis** (mode: market-share-capture-efficiency-and-execution-analysis)
9. **Indirect Competition and Substitution Threat Analysis** (mode: indirect-competition-and-substitution-threat-analysis)
10. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format


The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_competitive_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `peer-positioning`, `moat-analysis`, `share-shift`, `competitive-dynamics`). Examples:

- `LLY/2026-05-25_1430_competitive_peer-positioning.md`
- `NVDA/2026-05-25_1545_competitive_moat-analysis.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
