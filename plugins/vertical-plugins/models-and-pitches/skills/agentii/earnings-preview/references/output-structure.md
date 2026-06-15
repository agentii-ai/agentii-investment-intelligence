# earnings-preview — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

1. **Slide 1 — Title**: Company name, ticker, "Earnings Preview — Q<N> FY<YYYY>", report date
2. **Slide 2 — Company Overview**: Business description, sector, market cap, key products/segments (from `get_company_profile`)
3. **Slide 3 — Consensus Estimates**: Table with consensus/high/low for Revenue, EPS, EBITDA; YoY comparison; estimate count (from `search_earnings_calendar`)
4. **Slide 4 — Historical Surprises**: Table of last 4 quarters: estimate vs actual, surprise %, direction (from `search_earnings_calendar` + `search_xbrl_facts`)
5. **Slide 5 — Peer Comparison**: Peer table with ticker, EV/EBITDA, P/E, Revenue growth (from `search_companies` + `search_xbrl_facts`)
6. **Slide 6 — Catalysts & Outlook**: Forward catalysts from earnings transcript, upcoming events, guidance summary (from `search_earnings_calendar`)

Slide 6 is optional (4–6 range). If peer data or catalyst data is unavailable, merge into fewer slides.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
