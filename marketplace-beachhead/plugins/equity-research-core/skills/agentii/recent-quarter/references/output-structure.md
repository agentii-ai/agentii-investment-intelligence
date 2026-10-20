# recent-quarter — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** (≤200 words) — top-line revenue, EPS, key metrics for the quarter
2. **Consolidated P&L** (mode: consolidated-p-and-l) — revenue, gross profit, operating income, net income, diluted EPS with QoQ and YoY growth rates
3. **Margin Analysis** (mode: margin-analysis) — gross margin, operating margin, net margin trends across trailing 4 quarters
4. **Earnings vs. Consensus** (mode: earnings-vs-consensus) — EPS actual vs. estimated, surprise %, beat/miss streak
5. **Sequential Growth** (mode: sequential-growth) — QoQ growth rates for key line items
6. **Forward Outlook** (mode: forward-outlook) — guidance, consensus estimates, upcoming catalysts, earnings date
7. **Coverage Gaps & Citations** — cover what could not be retrieved; citations appear inline beside their facts (a bottom index is optional and never a repeat)

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; citations belong inline, a bottom roll-up index is optional and never a repeat of a link already given; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
