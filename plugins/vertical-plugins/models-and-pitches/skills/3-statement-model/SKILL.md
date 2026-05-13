---
name: 3-statement-model
description: >-
  3-statement integrated financial model: IS/BS/CFS triangulation, 5 historical + 5 forecast years, driver-based projection.
multi_ticker_semantics: single_target
parameter_free: false
---

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze 3 statement model
- run 3 statement model analysis
- produce 3 statement model report
- 3 statement model breakdown
- 3 statement model deep dive
- build a 3 statement model
- assess 3 statement model
- quantify 3 statement model
- compare 3 statement model across peers
- review 3 statement model for
- generate 3 statement model on
- 3 statement model for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

## Methodology

*This is a Phase 1 scaffold. Full methodology authored in Phase 3/4/5 (see tasks.md).*

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include per FR-020a: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
