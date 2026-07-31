---
name: macro-idea-generation
description: Macro-driven trade idea generation, translating macroeconomic views into concrete stock ideas, sector selection from macro regime, international trade ideas via ADRs, cross-border idea sourcing, macro catalyst mapping to equity positions
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "Macro regime shifts require multi-quarter context; 4 quarters default."
allowed_tools:
  - search_investment_strategies
  - get_investment_strategy
  - search_investment_cases
  - search_by_analogue
retrieval_scope: structured_only
layer_tags: ["L1", "L2"]
min_tool_diversity: 3
parameter_free: false
---

> Methodology fused from professional trading and investment frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| macro_signal_lag_weeks | 4-8 | Macro signals lead equity moves by 4-8 weeks |
| sector_mapping_depth | 3 | Three-tier cascade: regime → sector → stock |
| adr_liquidity_min | $10M ADTV | Minimum ADR liquidity for institutional execution |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Macro regime input — from `macro-analysis` skill (leading indicators, portfolio bias)
2. Sector data — sector-level performance, rotation signals from market data tools
3. ADR data — international equity access via ADRs from market data
4. Strategy frameworks — `search_investment_strategies(domain=macro)` + `search_by_analogue(market_regime=...)`

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Branch (d) Simple Lookup from `contracts/retrieval.md`: macro regime input from upstream skill. Sector and market data from data tools. Strategy frameworks and historical analogues via MCP knowledge tools. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

This skill translates macroeconomic views into concrete trade ideas via a three-tier cascade: Macro Regime → Sector Preference → Stock Selection. Macro tells you where to look; sectors what to look at; stocks what to trade.

Detailed methodology: regime-to-sector mapping matrix, ISM sector drilling protocol, inter-market confirmation framework, ADR screening and currency overlay, and macro risk invalidation rules are in `references/macro-ideas-methodology.md`.

**Core insight**: The "consensus disconnect" applies at the macro level — the market prices one regime, leading indicators suggest another emerging. This gap is the macro edge. Macro signals lead equity moves by 4-8 weeks.

#### Steps

1. **Macro Regime Translation**: Receive regime (expansion/contraction/stagflation/recovery) and bias (long/short/neutral) from upstream. Identify dominant theme: rate cycle, credit spreads, currency, commodities. Establish transmission mechanism — WHY sectors benefit or suffer, not just correlation.

2. **Sector Selection** (see reference for complete matrix with transmission mechanisms):
   - Expansion (ISM > 50 rising, credit tightening): Favor Tech, Consumer Disc, Industrials, Financials. Avoid Utilities, Staples.
   - Contraction (ISM < 50 falling, credit widening): Favor Utilities, Staples, Healthcare. Avoid Tech, Consumer Disc, Energy.
   - Stagflation (low growth + high inflation): Favor Energy, Materials, Commodity Producers, Healthcare. Avoid Consumer Disc, Real Estate.
   - Recovery (ISM crossing 50, central bank accommodative): Favor Financials, Industrials, Consumer Disc. This is historically the strongest equity return regime. Avoid prior defensives.

3. **Leading Indicator Deep Dive**:
   - **ISM PMI**: Headline + New Orders (leads by 1-3 months, most important sub-index) + Prices Paid + Supplier Deliveries. Drill sub-indices for industry divergence → pair trade signals.
   - **Yield Curve (10Y-2Y)**: Steepening > 150bp = Financials. Flattening = Growth/Tech. Inverted = defensive. Re-steepening from inverted = strongest rally phase.
   - **Credit Spreads (HY OAS)**: > 400bp = defensive regardless. 300-400bp = stock selection dominant. < 300bp = risk-on.
   - **DXY**: +5%/3mo = commodity/EM/multinational headwind. −5%/3mo = tailwind.

4. **Inter-Market Confirmation**: Bonds (yield curve, spreads) + Currencies (DXY, commodity FX) + Commodities (copper/gold, oil) must align. All three = high conviction. Two of three = medium, reduce 25-33%. All diverging = low, reduce/eliminate positions.

5. **Stock Selection**: Apply quant screening ONLY to 2-3 most favored and 2-3 most disfavored industries from ISM drilling. Prioritize companies where macro catalyst directly impacts business drivers (bank NIM from rate change = direct; tech multiple from rate change = indirect, less reliable).

6. **ADR International**: Country selection → screen ($10M ADTV, $500M cap, 20-F available). Avoid: Chinese software/computer services ADRs, micro-cap shipping, pharma/biotech (requires specialized expertise). Currency overlay: DXY strengthening → hedge or prefer domestic; weakening → unhedged benefit. ADR universe is mostly cyclical/old-economy. Split European banks investment/retail/hybrid.

7. **Macro Risk Management**: Define invalidation thresholds before entry (e.g., "ISM < 48 for 2 months = exit all cyclicals"). Post-event: 1 month divergence = noise; 2 months = trend change, exit. Total macro exposure ≤ 40%. Single sector ≤ 25%. If thesis invalidates, exit ALL macro positions simultaneously.

8. **MCP Integration**: `search_investment_strategies(domain=macro)` → `search_by_analogue(market_regime)` → `search_investment_cases(domain=macro_driven)`. Handoff: regime + conviction, sector matrix, top 3-5 stocks per sector, ADR candidates with FX assessment, macro catalyst timeline, invalidation thresholds.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_macro-idea-generation_{affix}.md`

## Output Structure

1. **Executive Summary** — Macro regime, inter-market confirmation status, top sectors, top 3 macro-driven trade ideas
2. **Macro Regime Analysis** — Current regime classification, dominant themes, transmission mechanisms, consensus disconnect assessment
3. **Leading Indicator Dashboard** — ISM (headline + New Orders + Prices Paid + industry sub-indices), yield curve, credit spreads, DXY, commodity signals
4. **Inter-Market Confirmation** — Bond/Currency/Commodity alignment assessment, conviction level, divergences flagged
5. **Sector Preference Matrix** — Favored/neutral/avoid sectors with macro rationale and transmission mechanism per sector
6. **Sector-Specific Stock Candidates** — Per preferred sector: macro sensitivity, valuation context, direct vs. indirect macro impact
7. **International Opportunities** — ADR candidates by country/region with currency overlay assessment, liquidity check, sector warnings
8. **Macro Catalyst Timeline** — Scheduled macro events (ISM, FOMC, employment, CPI) with expected impact and pre-positioning windows
9. **Historical Analogues** — Matched regime analogues from `search_by_analogue` with `/v/` citations, key parallels and divergences
10. **Risk to the Macro View** — Specific invalidation thresholds per indicator, correlation risk assessment, contingency exit protocol
11. **Handoff Summary** — Prioritized macro-driven ideas with conviction and sector rationale
12. **Coverage Gaps** — Data limitations, regions with insufficient ADR liquidity, sectors with inadequate macro data

## Error Handling

| Error | Fallback |
|-------|----------|
| No macro regime input | Derive from available macro data; flag as independently determined |
| ADR data insufficient | Limit to US-listed international ETFs as proxy; flag |
| `search_by_analogue` returns empty | Note "no historical regime analogues found"; proceed with framework only |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/macro-ideas-methodology.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`