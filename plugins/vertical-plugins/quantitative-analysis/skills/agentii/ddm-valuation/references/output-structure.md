# ddm-valuation — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — per-share fair value, premium/discount to current price, implied dividend yield
2. **Dividend Profile** — historical DPS, growth rate, payout ratio, coverage ratio, dividend consistency
3. **Cost of Equity** — CAPM decomposition: Rf, β, ERP → Ke
4. **Stage 1 — Explicit Forecast** — projected DPS per year with growth assumptions
5. **Stage 2 — Transition** — declining growth trajectory
6. **Stage 3 — Terminal Value** — Gordon Growth perpetuity
7. **Sensitivity** — fair value at varying Ke (±1%, ±2%) and terminal growth (±0.5%, ±1%)
8. **Applicability Note** — if dividends are irregular or newly initiated, flag model limitations
9. **Coverage Gaps & Citations**

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
