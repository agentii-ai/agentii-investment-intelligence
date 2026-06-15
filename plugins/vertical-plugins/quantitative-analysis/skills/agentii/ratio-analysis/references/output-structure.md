# ratio-analysis — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — top 3-5 ratios with interpretation, overall financial health assessment
2. **Profitability Analysis** — ROE, ROA, ROIC, margins table with trailing 4-quarter trend and industry comparison
3. **Liquidity Analysis** — current, quick, cash, operating CF ratios with short-term risk assessment
4. **Leverage Analysis** — D/E, interest coverage, debt/EBITDA with solvency assessment
5. **Efficiency Analysis** — asset turnover, inventory turnover, DSO, DIO with operational assessment
6. **Valuation Snapshot** — P/E (LTM+NTM), P/B, EV/EBITDA, P/S, PEG with sector peer comparison
7. **Growth Trends** — revenue/EPS CAGR (3yr + 5yr) with trend commentary
8. **Cross-Company Comparison** — peer ratio comparison table with mean/median/high/low (optional: --peers flag)
9. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
