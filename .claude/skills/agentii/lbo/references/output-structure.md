# lbo — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — sponsor IRR, MOIC, exit year, key value creation drivers (EBITDA growth, debt paydown, multiple expansion)
2. **Transaction Assumptions** — entry EBITDA, entry multiple, purchase price, debt/equity split, management equity rollover, transaction fees
3. **Sources & Uses** — sources (debt tranches, sponsor equity, management rollover) = uses (purchase price, fees, cash to B/S) within 0.1% (Validation Gate 1)
4. **Debt Schedule** — term loan, senior notes, subordinated notes, revolver: opening balance, mandatory repayments, optional repayments, interest rate, interest expense, closing balance per period (Validation Gate 3: mandatory repayments present for each tranche)
5. **Pro Forma Income Statement** — revenue, EBITDA, D&A, EBIT, interest expense, pre-tax income, net income per projection year
6. **Pro Forma Balance Sheet** — assets, debt tranches, equity accounts; calculation arc cross-validation per
7. **Cash Flow & Debt Paydown** — EBITDA → operating CF → total debt service → ending debt balances → cash generation
8. **Returns Waterfall** — enterprise value at exit → net debt at exit → equity value → sponsor equity return → IRR and MOIC
9. **Sensitivity Analysis** — 2-way table: entry multiple (rows) × exit multiple (columns) → IRR/MOIC matrix
10. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
