# business-model — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_business-model_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `product-line-decomp`, `channel-mix`, `market-sizing`, `management-changes`). Examples:

- `LLY/2026-05-25_1430_business-model_product-line-decomp.md`
- `NVDA/2026-05-25_1545_business-model_platform-classification.md`

The deliverable file MUST contain (in order):

1. **Executive Summary** (≤200 words) — business-model classification + headline structural insights.
2. **Business Model Type** (mode 1_1) — Product / Service / Platform classification with rationale.
3. **Product Line Decomposition** (mode 1_3) — revenue breakdown by product, top-3 contributors, concentration risk.
4. **Distribution Channel Analysis** (mode 1_2) — direct vs. indirect mix, partners, 3-year evolution.
5. **Customer Segment Analysis** (mode 1_3) — B2B vs. B2C, geography, end markets, concentration risk.
6. **Revenue Model** — recurring vs. one-time, pricing power, unit economics, gross-margin profile.
7. **Business Unit Performance** — segment-level P&L where available (XBRL or narrative).
8. **Market Sizing & Competitive Positioning** (mode 1_4) — TAM/SAM/SOM, relative growth vs. market.
9. **Management & Leadership** (mode 1_5) — executive team, recent changes, strategic implications.
10. **Coverage Gaps & Citations** — list of dimensions not retrievable + full citation index in `{ticker} {citation_id} page<N>` format.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
