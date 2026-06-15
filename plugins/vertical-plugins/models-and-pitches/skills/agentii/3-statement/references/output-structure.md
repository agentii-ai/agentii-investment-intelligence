# 3-statement — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — key model outputs (revenue CAGR, terminal EBITDA margin, ending cash balance), model integrity check results
2. **Historical Income Statement** (3-5 years) — revenue, COGS, gross profit, operating expenses, operating income, net income, diluted EPS with YoY growth rates
3. **Historical Balance Sheet** (3-5 years) — current assets, non-current assets, current liabilities, non-current liabilities, equity with period-over-period changes
4. **Historical Cash Flow** (3-5 years) — operating CF, investing CF, financing CF, net change in cash, ending cash balance
5. **Key Assumptions** — revenue growth rate, margin assumptions (gross/operating/net), working capital ratios (DSO, DIO, DPO), capex % of revenue, tax rate, dividend payout ratio
6. **Projected Income Statement** (5 forecast years) — same line items as historical with assumption-driven formulas
7. **Projected Balance Sheet** (5 forecast years) — same line items as historical; BS must balance within 1% per Validation Gate 1
8. **Projected Cash Flow** (5 forecast years) — same line items as historical; CF ending cash must tie to BS cash per Validation Gate 2
9. **Cross-Statement Validation** — balance check (A = L + E), cash tie-out, calculation arc cross-validation , inter-statement consistency
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
