# Preflight Contract (shared include)

Canonical pre-flight sequence for every agentii skill. Skills reference this file
with a one-line `## Preflight` pointer instead of inlining the steps. Written ONCE
here so the probe, ticker-resolution, and workspace-override logic never drift
across the 31 skills.

## Step 0 — MCP health probe

Run the health probe before any retrieval. If it returns `UNREACHABLE`, halt with
the Error Handling "MCP unreachable" policy:

```
!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"
```

## Step 1 — Ticker resolution

Before any data retrieval, resolve the ticker via the three-layer fallback:

1. Exact match via `search_companies(ticker=<input>)`.
2. `pg_trgm` fuzzy alias match via `gold.entity_aliases` (6,721 rows).
3. Share-class normalization for multi-class tickers (GOOG/GOOGL→GOOG,
   BRK.A/BRK.B→BRK.B).

Return the canonical ticker, match method, and a confidence indicator.

## Step 2 — Workspace `style.md` override check

Check `./style.md` in the workspace root for per-workspace overrides
(`default_lookback_quarters`, `reporting_currency`, `sector_focus`,
`output_verbosity`, `peer_universe`). Apply overrides to output formatting and
temporal scope.

Precedence: workspace `style.md` > package `style.md` > skill defaults.

## Step 3 — Memory load

Execute the `contracts/memory-load.md` glob-and-summarize step so prior
conclusions for this ticker are in context before retrieval begins.

## Step 4 — Coverage check

Call `get_company_fiscal_calendar/{ticker}` for fiscal orientation, then
`get_ticker_coverage/{ticker}` to discover which data sources are populated, and
route retrieval accordingly.

## Agent Call Tracing

The canonical tracing text lives in the agent system prompt
(`plugins/agent-plugins/agentii-equity-agent/agents/agentii-equity-agent.md`).
Skills reference `contracts/x-agentii-trace-header.md` in one line; do not inline
the tracing block.
