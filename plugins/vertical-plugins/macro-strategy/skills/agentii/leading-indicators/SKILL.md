---
name: leading-indicators
description: Leading economic indicators analysis, ISM PMI, yield curve, consumer sentiment UMCSI, jobless claims, building permits, economic turning point detection, recession signal analysis
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters default for leading-indicators analysis; up to 12 for regime context."
allowed_tools:
  - search_knowledge_entries
  - get_knowledge_entry
  - search_by_analogue
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught trading frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| lookback_quarters | 4 | Standard window for leading-indicators |
| gdp_forecast_lag | 6 months | S&P 500 leads GDP with maximum statistical significance at the 6-month horizon (10-year rolling correlation avg: 0.56, 1960–2020) |
| indicator_frequency | weekly | Money-market and survey indicators are tracked weekly; GDP is quarterly |
| portfolio_bias | long / neutral / short | Macro view resolves to one of three biases governing portfolio construction |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Leading indicators framework — `references/leading-indicators-framework.md` (bundled methodology)
2. Knowledge entries — query `search_knowledge_entries` for supplementary L1 frameworks
3. Historical analogues — query `search_by_analogue(market_regime, event_type)`
4. Real-time data — FRED (real rates, yield curve, money supply, credit spreads), ISM PMI, UMCSI, jobless claims, building permits, commodity prices, DXY

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
This skill follows Branch (d) Simple Lookup from `contracts/retrieval.md`: query knowledge entries for L1 macro and leading-indicator frameworks; query `search_by_analogue` for historical regime analogues resolved from the indicator panel. No unstructured document retrieval.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol

The Pro-Trader Systematic macroeconomic framework: **predict GDP → predict stock-market returns**. S&P 500 leads GDP by 6 months (10-year rolling correlation avg 0.56). Two analytical axes: **Growth** drives earnings (E); **Liquidity** drives price (P). Detailed indicator methodology, thresholds, and decision rules are in `references/leading-indicators-framework.md`.

1. **GDP Baseline**: Quadrinomial method (S&P 500 quarterly returns 6-month lagged vs real GDP). Four outcomes: 0-0 (both down, 8.2%), 1-1 (both up, 60.9%), 0-1 (profit-taking, 25.6%), 1-0 (unpredictable, 5.3%). 10-year rolling correlation check. Apply to EuroStoxx 600 vs Eurozone GDP. Skip China Shenzhen (unreliable correlation ~0.05).

2. **Money Market Indicators** (earliest and most reliable):
   - **Real interest rates**: Nominal rate − CPI. Classify accommodative (< 0.5%), neutral (0.5–2%), restrictive (> 2%). Direction: falling = bullish; rising = bearish.
   - **Yield curve (2s10s)**: Normal/steep = expansionary. Flattening = transition. Inverted = recession (6–18 month lead). Steepening from inversion = recovery. Monitor TED spread (3m LIBOR vs 3m Treasury) for global dollar stress.
   - **Credit spreads**: Hierarchy AA (ICE BofA, FRED) → BBB → CCC (junk moves first). Widening = contractionary → sell. Tightening = expansionary → buy. CCC blowout 400+ bps with AA calm = stress concentration.
   - **M2 Money Supply**: Accessory only. Accelerating + falling real rates = confirm expansion. Decelerating + rising real rates = confirm contraction. Divergence = flag regime ambiguity.

3. **Survey Indicators**:
   - **ISM Manufacturing PMI**: > 50 expansion, < 50 contraction. Prioritize New Orders sub-component. PMI < 45 = strong contraction.
   - **UMCSI Consumer Sentiment**: < 70 recession warning, > 90 confident. Sharp MoM drops > 5 points often precede equity corrections.

4. **Commodity Prices**: Copper (pervasive industrial demand proxy — compare LME vs Shanghai). Brent crude (rising with copper = demand-driven, bullish; rising without copper = supply shock, bearish).

5. **Market & Forex**: S&P 500 as ultimate daily leading indicator. DXY strengthening = tightening global conditions; weakening = loosening. Cross-reference DXY direction against credit spread direction.

6. **Coincident & Lagging Cross-Check**: CPI, PPI, NFP (coincident); GDP, earnings, unemployment (lagging). Never trade on lagging indicators alone.

7. **International**: European ESI, China PMI (Official vs Caixin — Caixin often leads), Japan Tankan + JGB, UK Gilts + PMI, Germany Bund + Ifo, Italy BTP-Bund spread. Apply local CPI for real rates.

8. **Dashboard & Bias Resolution**: Score 11 indicator categories (high-weight: real rates, yield curve, credit spreads, ISM PMI, S&P 500). ≥ 60% expansionary → net long. ≥ 60% contractionary → net short. Mixed → neutral.

9. **Analogue Retrieval**: Query `search_by_analogue` with `market_regime` and `event_type` matching current configuration. Cite via `/v/`.

10. **Regime Classification**: Expansion / Contraction / Stagflation / Recovery with Bear/Base/Bull probability weights and transition catalysts.

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_leading-indicators_{affix}.md`

## Output Structure

1. **Executive Summary** — GDP forecast (6-month forward), portfolio bias (long / neutral / short), regime classification with probability weights, top 3 signals in 2–3 sentences
2. **GDP Baseline** — quadrinomial quadrant assignment, rolling correlation trend (S&P 500 vs GDP, 6-month lag), international comparison (Eurozone, China)
3. **Money Market Indicators** — real interest rates (current level + direction), yield curve 2s10s (shape + direction), credit spreads (AA / BBB / CCC spreads over 10Y, direction + magnitude), M2 money supply growth (trend)
4. **Survey Indicators** — ISM Manufacturing PMI (headline + new orders), UMCSI consumer sentiment (headline + expectations)
5. **Commodity & Market Signals** — copper, Brent crude, S&P 500 quarterly direction, DXY trend
6. **International Context** — European ESI, China PMI (official vs Caixin), other major economy indicators
7. **Leading Indicator Dashboard** — weighted scorecard table with expansionary/contractionary signal count
8. **Regime Classification** — regime type (Expansion / Contraction / Stagflation / Recovery), probability weights (Bear / Base / Bull), transition catalysts
9. **Portfolio Bias Recommendation** — net long / net short / neutral with supporting evidence
10. **Historical Analogues** — matched cases from `search_by_analogue` with `/v/` citations
11. **Risk Assessment & Caveats** — Fed intervention risk, signal divergence flags, data limitations
12. **Coverage Gaps** — indicators with stale / missing data; degraded-mode annotations

## Error Handling

| Error | Fallback |
|-------|----------|
| No L1 frameworks found | Proceed with the standard 10-indicator panel described in Protocol; flag degraded |
| `search_by_analogue` empty | Note "no relevant historical analogues found" — do not fabricate |
| Real-time data unavailable | Use last-known values with staleness flag; indicate date of last observation |
| Credit spread data missing for one tier | Use available tiers (AA/BBB) and note the gap; CCC data is most volatile and optional |
| Yield curve data flat / 2Y missing | Use 3m10y or Fed funds vs 10Y as alternative curve; note substitution |
| International indicator missing | Proceed with US-only dashboard; flag international gap |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `references/leading-indicators-framework.md`
- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `contracts/retrieval.md`
