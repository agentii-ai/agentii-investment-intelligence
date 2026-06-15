# dcf — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — intrinsic value per share, upside/downside vs. current price, key value drivers, WACC used
2. **Key Assumptions** — risk-free rate, equity risk premium, beta, cost of equity (Ke), cost of debt (Kd), target capital structure, WACC, terminal growth rate, projection period (≥5 years per Validation Gate 1)
3. **Unlevered Free Cash Flow Projection** — EBIT → NOPAT → D&A add-back → Capex → Working Capital Changes → UFCF for each projection year with YoY growth rates
4. **Terminal Value** — Gordon Growth Model: TV = UFCF(n+1) / (WACC - g). Terminal growth rate must be < risk-free rate (Validation Gate 2)
5. **Enterprise Value** — PV of projected UFCFs + PV of Terminal Value. Mid-year convention applied where appropriate
6. **Equity Value Bridge** — Enterprise Value - Net Debt + Cash - Minority Interest → Equity Value
7. **Per-Share Value** — Equity Value / Fully Diluted Shares Outstanding → intrinsic value per share
8. **Sensitivity Analysis** — 2-way data table: WACC (rows) × Terminal Growth Rate (columns) → per-share value matrix
9. **Calculation Arc Cross-Validation ** — income statement structure verified against `gold.xbrl_calculations` weights; FCF drivers aligned with historical margins from XBRL
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
