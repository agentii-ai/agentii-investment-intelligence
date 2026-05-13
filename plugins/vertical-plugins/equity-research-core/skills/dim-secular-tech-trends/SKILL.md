---
name: dim-secular-tech-trends
description: >-
  Secular technology trend analysis: AI adoption, platform shifts, data-infrastructure exposure, and long-duration tailwind assessment.
multi_ticker_semantics: target_with_optional_peers
parameter_free: false
---

<!-- analog: idea-generation -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

- analyze dim secular tech trends
- run dim secular tech trends analysis
- produce dim secular tech trends report
- dim secular tech trends breakdown
- dim secular tech trends deep dive
- build a dim secular tech trends
- assess dim secular tech trends
- quantify dim secular tech trends
- compare dim secular tech trends across peers
- review dim secular tech trends for
- generate dim secular tech trends on
- dim secular tech trends for investment decision

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
