# peg-valuation — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — PEG (LTM + NTM), rating, 1-sentence investment implication
2. **PEG Computation** — P/E numerator breakdown (LTM, NTM), growth rate denominator (source: consensus or historical CAGR), PEG result
3. **Growth Rate Analysis** — consensus LTG vs historical CAGR, growth quality assessment (sustainable? accelerating? decelerating?)
4. **Sector PEG Comparison** — peer PEG table with mean/median/high/low, target's percentile rank
5. **Sensitivity** — PEG at varying growth rates (±5%, ±10%, ±20% from base case)
6. **Limitations** — PEG not meaningful for cyclical, negative earnings, or zero-growth companies
7. **Coverage Gaps & Citations** — data sources + citation index

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
