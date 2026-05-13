---
name: dim-earnings-sentiment
description: >-
  Earnings sentiment analysis: transcript tone, Q&A dynamics, management confidence signals, and sell-side estimate revision patterns.
multi_ticker_semantics: single_target
parameter_free: false
---

<!-- analog: catalyst-calendar -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim earnings sentiment
- run dim earnings sentiment analysis
- produce dim earnings sentiment report
- dim earnings sentiment breakdown
- dim earnings sentiment deep dive
- build a dim earnings sentiment
- assess dim earnings sentiment
- quantify dim earnings sentiment
- compare dim earnings sentiment across peers
- review dim earnings sentiment for
- generate dim earnings sentiment on
- dim earnings sentiment for investment decision

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
