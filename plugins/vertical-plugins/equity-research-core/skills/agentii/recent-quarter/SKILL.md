---
name: recent-quarter
multi_ticker_semantics: single_target
description: Recent quarter performance analysis, quarterly earnings review, last quarter results, quarterly financial performance, analyze recent quarter, Q4 earnings, quarterly revenue breakdown, EPS this quarter, margin analysis recent quarter, sequential growth, quarterly performance review
temporal_scope:
 default_quarters: 1
 max_quarters: 4
 description: "Recent quarter analysis focuses on the most recent quarter's P&L. Max 4 quarters for sequential trend."
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - get_company_financials
 - get_company_profile
 - search_earnings_calendar
 - get_company_fiscal_calendar
 - get_ticker_coverage
 - list_xbrl_concepts
 - batch_search
retrieval_scope: structured_only
min_tool_diversity: 6
---

# Recent Quarter Performance

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze recent quarter performance for {ticker}
- quarterly earnings review for {ticker}
- last quarter results {ticker}
- quarterly financial performance {ticker}
- analyze {ticker} recent quarter
- {ticker} Q4 earnings
- {ticker} quarterly revenue breakdown
- EPS this quarter {ticker}
- margin analysis recent quarter {ticker}
- sequential growth {ticker}

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| lookback_quarters | 1 | Single most-recent quarter |
| include_sequential | true | Show QoQ growth rates |

## Methodology

### 1. Retrieval Scope

This skill performs **structured data retrieval only** (XBRL facts + earnings calendar). No unstructured document search — business-model structural analysis is handled by `/agentii:business-model` . This skill is TEMPORAL/QUANTITATIVE .

### 2. Retrieval Strategy

1. ** Pre-flight (mandatory)**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`. Route based on coverage.
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest])` — returns `is_primary: true` rows by default.
3. **Earnings calendar**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])` — returns EPS actual/estimate/surprise. Use `get_company_fiscal_calendar` for fiscal period orientation, NOT `search_earnings_calendar` .
4. **Consolidated P&L**: `get_company_financials/{ticker}` returns IS/BS/CF highlights with XBRL data.

### 3. Temporal Scope

Default: 1 fiscal quarter (max 4). This skill is a temporal snapshot of the most recent quarter's financial performance.

### 4. Tool Allowlist

See frontmatter `allowed_tools` — 7 tools declared for this dimension. This skill is `structured_only` (temporal/quantitative only). `search_xbrl_facts` is the primary data source for consolidated P&L metrics. `search_earnings_calendar` provides EPS actuals, estimates, and surprise data. `get_company_fiscal_calendar` resolves fiscal period orientation. Document search and structural analysis belong to `/agentii:business-model` .

### 5. Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format, then `get_ticker_coverage/{ticker}` .
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest])` — returns `is_primary: true` rows by default.
3. **Earnings calendar**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])` for EPS actuals, estimates, and surprise percentages.
4. **Financial highlights**: `get_company_financials/{ticker}` for IS/BS/CF summary data.
5. **Output**: produce P&L progression table with QoQ and YoY growth rates, margin trend chart data, and earnings-vs-consensus comparison.

## Modes (5 — temporal / quantitative)

**This skill is temporal/quantitative ONLY.** Structural analysis (business model classification, product-line decomposition, channel analysis) belongs to `/agentii:business-model` . Modes below focus on quarterly P&L data, growth rates, margins, and earnings vs. consensus.

### Mode: consolidated-p-and-l (essentials)

**Display name**: Consolidated P&L Progression

**Objective**: Extract and present the most recent quarter's consolidated P&L — revenue, gross profit, operating income, net income, diluted EPS — with sequential (QoQ) and year-over-year (YoY) growth rates.

**Tool calls**: `get_company_financials/{ticker}`, `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss"], fiscal_year=[latest], fiscal_period=[latest])`

**Output**: Consolidated P&L table with QoQ and YoY growth rates. Citation format: `{ticker} {citation_id} page<N>`.

### Mode: margin-analysis (essentials)

**Display name**: Margin Analysis

**Objective**: Track gross margin, operating margin, and net margin across the most recent 4 quarters. Identify trends, inflection points, and drivers (pricing power, cost structure changes, operating leverage).

**Tool calls**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss"], fiscal_year=[latest, latest-1])`

**Output**: Margin trend table with QoQ deltas. Commentary on margin drivers.

### Mode: earnings-vs-consensus

**Display name**: Earnings vs. Consensus

**Objective**: Compare actual EPS against consensus estimates for the most recent quarter. Present surprise %, beat/miss track record (trailing 4 quarters), and guidance accuracy.

**Tool calls**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])`

**Output**: EPS actual vs. estimated table with surprise % and beat/miss streak.

### Mode: sequential-growth

**Display name**: Sequential Growth Analysis

**Objective**: Compute quarter-over-quarter growth rates for revenue, gross profit, operating income, and EPS across the trailing 4 quarters. Highlight accelerating or decelerating trends.

**Tool calls**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest, latest-1])`

**Output**: Sequential growth rate table with trend arrows and inflection detection.

### Mode: forward-outlook

**Display name**: Forward Outlook & Guidance

**Objective**: Extract management guidance for the upcoming quarter, upcoming earnings date, consensus estimates for next quarter, and key catalysts (product launches, regulatory events, earnings announcements).

**Tool calls**: `search_earnings_calendar(ticker, upcoming=true)`, `get_company_financials/{ticker}` (for guidance narrative)

**Output**: Forward outlook summary with guidance, consensus, upcoming catalysts, and earnings date.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `search_xbrl_facts` | Empty result | Try prior fiscal year; if still empty, flag as data-unavailable | "XBRL facts unavailable for this ticker/period" |
| `search_earnings_calendar` | Empty result | Use `get_company_fiscal_calendar` to determine correct fiscal period format | "Earnings calendar unavailable; using fiscal calendar for period orientation" |
| `get_company_financials` | 404 / error | Use individual `search_xbrl_facts` calls for each concept | "Financials overview unavailable; using granular XBRL facts" |

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_recent-quarter_{affix}.md` . Example affixes: `consolidated-p-and-l`, `margin-trends`, `earnings-vs-consensus`.

## Output Structure

1. **Executive Summary** (≤200 words) — top-line revenue, EPS, key metrics for the quarter
2. **Consolidated P&L** (mode: consolidated-p-and-l) — revenue, gross profit, operating income, net income, diluted EPS with QoQ and YoY growth rates
3. **Margin Analysis** (mode: margin-analysis) — gross margin, operating margin, net margin trends across trailing 4 quarters
4. **Earnings vs. Consensus** (mode: earnings-vs-consensus) — EPS actual vs. estimated, surprise %, beat/miss streak
5. **Sequential Growth** (mode: sequential-growth) — QoQ growth rates for key line items
6. **Forward Outlook** (mode: forward-outlook) — guidance, consensus estimates, upcoming catalysts, earnings date
7. **Coverage Gaps & Citations** — data not retrievable + citation index in `{ticker} {citation_id} page<N>` format

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-Q p.12](https://agentii.ai/v/LLY/sec178/12)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|-------------|-----------|--------|---------------------|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
