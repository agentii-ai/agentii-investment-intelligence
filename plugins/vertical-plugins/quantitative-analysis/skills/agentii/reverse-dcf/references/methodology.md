# reverse-dcf — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch: **(a) Structured Data Query**. Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.

## Protocol

1. **Inputs**: current stock price from `get_realtime_quote(ticker)`. Shares outstanding and latest financials from `search_xbrl_facts`.
2. **Set up DCF model**: standard DCF with UFCF = EBIT × (1-T) + D&A - Capex - ΔWC. Terminal value via Gordon Growth Model.
3. **Solve for implied growth rate**: iterate growth rate until DCF fair value = current market price (within 1% tolerance).
4. **Solve for implied terminal margin**: if solving for margin, iterate terminal EBITDA/FCF margin instead.
5. **Solve for implied WACC**: if solving for WACC, iterate WACC until DCF = market price (reveals market-implied discount rate).
6. **Compare to benchmarks**:
 - Implied growth vs. consensus estimates (from `search_earnings_calendar`)
 - Implied growth vs. historical CAGR (from XBRL)
 - Implied margin vs. current margin + historical trend
 - Implied WACC vs. CAPM-derived WACC
7. **Assessment**: flag when market prices in >20% above consensus (potentially overvalued) or >20% below consensus (potentially undervalued).
8. **Output**: per with YAML frontmatter .
