# secular-trends — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

**Sections** (this skill's own declared elements; each maps to the modes in
`references/modes.md`, which carry the per-mode focus and tool list):

1. **Executive Summary** (≤200 words) — headline conclusions for this dimension
2. **Evaluate Company's Exposure to Major Secular Technology Trends** (mode: evaluate-company-s-exposure-to-major-secular-technology-trends)
3. **Deep Dive Ai Trend Assessment for Companies with Identified Ai Exposure** (mode: deep-dive-ai-trend-assessment-for-companies-with-identified-ai-exposure)
4. **Deep Dive Data Value Trend Assessment for Companies with Identified Data Exposure** (mode: deep-dive-data-value-trend-assessment-for-companies-with-identified-data-exposure)
5. **Deep Dive Ev Trend Assessment for Companies with Identified Ev Exposure** (mode: deep-dive-ev-trend-assessment-for-companies-with-identified-ev-exposure)
6. **Deep Dive Analysis for Quantum Computing Renewable Energy and Other Emerging Tech Trends** (mode: deep-dive-analysis-for-quantum-computing-renewable-energy-and-other-emerging-tech-trends)
7. **Evaluate Company's Strategic Position Within Identified Technology Trends** (mode: evaluate-company-s-strategic-position-within-identified-technology-trends)
8. **Evaluate Company's Capacity and Readiness to Invest in Technology Transformation** (mode: evaluate-company-s-capacity-and-readiness-to-invest-in-technology-transformation)
9. **Assess the Significance of Technology Trends in Current Investment Debate and Market Perception** (mode: assess-the-significance-of-technology-trends-in-current-investment-debate-and-market-perception)
10. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format


The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_secular-trends_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `trend-impact`, `tailwind-headwind`, `theme-exposure`, `secular-positioning`). Examples:

- `LLY/2026-05-25_1430_secular-trends_trend-impact.md`
- `NVDA/2026-05-25_1545_secular-trends_theme-exposure.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
