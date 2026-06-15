# comps — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Executive Summary** — target company's relative valuation conclusion (premium/discount/fair vs. peers), key multiple that drives the spread
2. **Peer Selection Rationale** — 4-8 peers (Validation Gate 1), sector/industry alignment, size proximity (market cap, revenue scale), business model comparability
3. **Company Profiles** — one paragraph per peer: ticker, market cap, revenue, EBITDA, key business segments, 1-sentence differentiation from target
4. **Trading Multiples Table** — P/E (LTM + NTM), EV/EBITDA (LTM + NTM), EV/Revenue, P/B, PEG ratio for each peer (Validation Gate 2: EV/EBITDA + P/E at minimum)
5. **Valuation Summary** — mean, median, high, low for each multiple (Validation Gate 3: statistics table mandatory). Implied valuation range for target
6. **Relative Value Assessment** — target vs. peer median: premium/discount analysis, justified premium factors (growth, margins, moat), unjustified discount factors (overhang, complexity)
7. **Cross-Company Comparability Notes** — concept availability verified (`get_statement_structure` for each peer), accounting differences flagged, fiscal-year misalignment noted
8. **Coverage Gaps & Citations** — data not retrievable + full citation index in `{ticker} {citation_id} page<N>` format

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
