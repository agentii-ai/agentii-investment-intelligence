---
name: dcf-model
description: >-
  DCF valuation model: 5-10 year projection, terminal value, WACC construction, and sensitivity tables. All projection/margin/discount/PV cells must be live formulas (FR-020/FR-044 hard gate).
multi_ticker_semantics: single_target
parameter_free: false
---

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dcf model
- run dcf model analysis
- produce dcf model report
- dcf model breakdown
- dcf model deep dive
- build a dcf model
- assess dcf model
- quantify dcf model
- compare dcf model across peers
- review dcf model for
- generate dcf model on
- dcf model for investment decision

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
