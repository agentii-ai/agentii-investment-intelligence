---
name: growth-strategy
description: Growth strategy analysis, organic growth decomposition, inorganic growth, M&A strategy, pipeline analysis, revenue growth drivers, strategic initiatives, expansion strategy, growth trajectory, product pipeline growth
temporal_scope:
 default_quarters: 4
 max_quarters: 10
 description: "Typical lookback: 4 quarters, max: 10"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_documents
 - search_sec_filings
 - get_company_financials
 - get_company_profile
 - list_coverage
 - read_source_outline
 - list_xbrl_concepts
 - read_source_pages
 - search_keyword_in_source
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: initiating-coverage -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution **: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

**Workspace style.md override check **: Check `./style.md` in the workspace root for per-workspace overrides (`default_lookback_quarters`, `reporting_currency`, `sector_focus`, `output_verbosity`, `peer_universe`). Apply overrides to output formatting and temporal scope. Precedence: workspace `style.md` > package `style.md` > skill defaults.


**Agent Call Tracing**: The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically. When spawning parallel sub-agents of the same type, assign each a unique instance label (e.g., equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for the full contract.
## Triggers

- analyze dim growth strategy
- run dim growth strategy analysis
- produce dim growth strategy report
- dim growth strategy breakdown
- dim growth strategy deep dive
- build a dim growth strategy
- assess dim growth strategy
- quantify dim growth strategy
- compare dim growth strategy across peers
- review dim growth strategy for
- generate dim growth strategy on
- dim growth strategy for investment decision

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

<!-- BEGIN port-dimension-prompts methodology + modes -->

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_labels=financial_results_2_02,material_definitive_agreement_1_01` to surface growth-investment-related 8-Ks (capex commitments, M&A, partnerships) before Layer 2.

### Temporal Scope

Default: 8 fiscal quarters (max 16). Growth strategy: 8 quarters for organic/inorganic growth trend decomposition

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 5 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: growth-strategy-assessment

**Display name**: growth-strategy-assessment

<!-- ported_from: references/prompts/3/3_1.yaml -->

**Focus**: Systematically analyze company's growth strategy by evaluating multiple data sources.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

 - citations
 - clarity
 - conciseness
 - evidence_based
 - recency
- **structure**: ## Growth Strategy Assessment

**Growth Strategy Classification**: [Organic / Inorganic / Mix]

**Strategy Summary**:
{Concise explanation of the company's growth approach, 3-5 sentences}

**Supporting Evidence**:

### Organic Growth Indicators
- {List identified organic initiatives with citations}
- {Example: Product development programs mentioned in Q2 earnings call _(cite source filing in standard agentii citation format at runtime)_}

### Inorganic Growth Indicators
- {List identified inorganic initiatives with citations}
- {Example: M&A transaction announced in 8-K filing _(cite source filing in standard agentii citation format at runtime)_}

**Data Sources Analyzed**:
- {List key documents reviewed: 10-K, earnings calls, analyst reports}

**Temporal Scope**: {Specify analysis period, e.g., "FY23 10-K plus Q1-Q2 2024 earnings materials"}

### Mode: organic-growth-drivers-analysis

**Display name**: organic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_2_1.yaml -->

**Focus**: Systematically identify and extract organic growth drivers across 6 dimensions.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`

 - citation_discipline
 - evidence_requirements
 - presence_determination
 - temporal_accuracy
- **structure**: ## Organic Growth Drivers Analysis

**Analysis Period**: {Specify fiscal quarters analyzed, e.g., "2024 Q1-Q2"}

**Data Sources**:
- Most Recent 10-K: {Filing date}
- Quarterly Materials: {List earnings calls, 10-Qs analyzed}
- Sell-Side Research: {List analyst reports reviewed}

**Growth Driver Assessment**:

| Dimension | Presence | Summary of Evidence | Source(s) |
|:----------|:---------|:-------------------|:----------|
| Product | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Market | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Customer Retention | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Pricing | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Sales & Channel | Yes/No/Nil | {Brief description of initiatives} | {Citations} |
| Marketing | Yes/No/Nil | {Brief description of initiatives} | {Citations} |

**Detailed Evidence**:

### Product
{If Presence=Yes, provide detailed description}
- Initiative 1: {Description} _(cite source filing in standard agentii citation format at runtime)_
- Initiative 2: {Description} _(cite source filing in standard agentii citation format at runtime)_

{Repeat for each dimension with Presence=Yes}

**Key Observations**:
- {Synthesize overall organic growth approach}
- {Note any patterns or emphasis across dimensions}

### Mode: organic-growth-driver-execution-assessment

**Display name**: organic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_2_2.yaml -->

**Focus**: Assess the execution progress of previously identified organic growth drivers.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

 - citation_discipline
 - evidence_requirements
 - status_determination
 - temporal_accuracy
- **structure**: ## Organic Growth Driver Execution Progress Assessment

**Assessment Period**: {Most recent fiscal quarter, e.g., "2024 Q2"}
**Assessment Date**: {Latest earnings date used for analysis}

**Data Sources**:
- Latest Earnings Call: {Date and quarter}
- Most Recent 10-Q: {Filing date}
- Sell-Side Research: {List recent analyst reports reviewed}

**Execution Status Summary**:

| Growth Driver | Execution Status | Summary of Progress / Commentary | Source(s) |
|:--------------|:-----------------|:--------------------------------|:----------|
| Product | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Market | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Customer Retention | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Pricing | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Sales & Channel | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |
| Marketing | On Track / Behind / Ahead | {Key progress points and evidence} | {Citations} |

**Detailed Execution Evidence**:

### {Dimension Name}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Initiative** (from task 3_2_1):
{Brief recap of initiative identified previously}

**Current Progress**:
- Evidence Point 1: {Description with metrics} _(cite source filing in standard agentii citation format at runtime)_
- Evidence Point 2: {Description with metrics} _(cite source filing in standard agentii citation format at runtime)_
- Management Commentary: {Relevant quote or summary} _(cite source filing in standard agentii citation format at runtime)_

**Status Rationale**:
{Explanation of why this status was assigned based on evidence}

{Repeat for each dimension with Presence=Yes}

**Overall Execution Assessment**:
- {Synthesize execution progress across all organic growth drivers}
- {Note any patterns: most initiatives on track, specific areas of concern, etc.}
- {Highlight any dimension showing particularly strong or weak execution}

### Mode: inorganic-growth-drivers-analysis

**Display name**: inorganic-growth-drivers-analysis

<!-- ported_from: references/prompts/3/3_3_1.yaml -->

**Focus**: Systematically identify and extract inorganic growth drivers over the past 5 years.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`

 - chronological_accuracy
 - citation_discipline
 - impact_assessment_rigor
 - presence_determination
 - transaction_completeness
- **structure**: ## Inorganic Growth Drivers Analysis

**Analysis Period**: {Specify 5-year period, e.g., "FY19-FY23 plus 2024 YTD"}

**Data Sources**:
- Annual Filings: {List 10-K years reviewed}
- Material Announcements: {Number of 8-Ks reviewed}
- Earnings Materials: {Recent earnings calls reviewed}

**Inorganic Activity Assessment**:

| Dimension | Presence | Summary of Evidence | Impact | Source(s) |
|:----------|:---------|:-------------------|:-------|:----------|
| M&A Transactions | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Equity Investments | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Asset Purchases | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Divestitures | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Strategic Alliances / JVs | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |
| Licensing / Franchise Deals | Yes/No/Nil | {Count and brief overview} | {Predominant impact category} | {Citations} |

**Detailed Transaction Listings**:

### {Category Name}
**Presence**: Yes/No/Nil

{If Presence=Yes, provide chronological listing}

#### Transaction 1: {Acquired Company / Asset / Partner Name}
- **Date**: {Announcement date} | {Closing date}
- **Transaction Type**: {Acquisition / Investment / Alliance / etc.}
- **Description**: {Brief description of target and strategic rationale}
- **Financial Terms**: {Purchase price, structure, ownership %}
- **Strategic Rationale**: {Why this transaction supports growth strategy}
- **Impact Assessment**: Factor-in / On-going / Unclear
 - {Explanation of impact assessment}
 - {Revenue contribution, synergies, integration status}
- **Sources**: _(cite source filing in standard agentii citation format at runtime)_, _(cite source filing in standard agentii citation format at runtime)_

#### Transaction 2: {Name}
{Repeat structure for each transaction}

{Repeat for each category with Presence=Yes}

**Key Observations**:
- {Total count of inorganic activities across all categories}
- {Dominant inorganic growth approach: M&A, partnerships, etc.}
- {Evolution of strategy over 5 years: increasing/decreasing activity}
- {Current vs. historical impact: how much of growth is factored in}

### Mode: inorganic-growth-driver-execution-assessment

**Display name**: inorganic-growth-driver-execution-assessment

<!-- ported_from: references/prompts/3/3_3_2.yaml -->

**Focus**: Assess the execution progress of previously identified inorganic growth drivers.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`

 - citation_discipline
 - evidence_requirements
 - status_determination
 - temporal_accuracy
- **structure**: ## Inorganic Growth Driver Execution Progress Assessment

**Assessment Period**: {Most recent fiscal quarter, e.g., "2024 Q2"}
**Assessment Date**: {Latest earnings date used for analysis}

**Data Sources**:
- Latest Earnings Call: {Date and quarter}
- Most Recent 10-Q: {Filing date}
- Sell-Side Research: {List recent analyst reports reviewed}

**Execution Status Summary**:

| Growth Driver | Execution Status | Summary of Progress / Commentary | Source(s) |
|:--------------|:-----------------|:--------------------------------|:----------|
| M&A Transactions | On Track / Behind / Ahead | {Key integration progress and synergy realization} | {Citations} |
| Equity Investments | On Track / Behind / Ahead | {Commercial benefits and strategic value realization} | {Citations} |
| Strategic Alliances / JVs | On Track / Behind / Ahead | {Operational progress and revenue contribution} | {Citations} |
| Licensing Agreements | On Track / Behind / Ahead | {Royalty realization and technology access} | {Citations} |
| Asset Purchases | On Track / Behind / Ahead | {Capacity ramp and revenue contribution} | {Citations} |
| Divestitures | On Track / Behind / Ahead | {TSA completion and capital redeployment} | {Citations} |

**Detailed Execution Evidence**:

### {Transaction Name or Category}
**Status**: On Track / Behind Schedule / Ahead of Plan

**Original Transaction** (from task 3_3_1):
{Brief recap: date, type, size, strategic rationale}

**Original Expectations**:
{Integration timeline, synergy targets, or other stated goals}

**Current Progress**:

#### Organizational Integration
- Evidence Point 1: {Leadership retention, employee metrics} _(cite source filing in standard agentii citation format at runtime)_
- Evidence Point 2: {Organizational structure changes} _(cite source filing in standard agentii citation format at runtime)_

#### Systems and Operations
- Evidence Point 1: {IT integration status, system cutover milestones} _(cite source filing in standard agentii citation format at runtime)_
- Evidence Point 2: {Process harmonization progress} _(cite source filing in standard agentii citation format at runtime)_

#### Commercial Integration
- Evidence Point 1: {Customer retention metrics} _(cite source filing in standard agentii citation format at runtime)_
- Evidence Point 2: {Cross-sell or revenue synergy progress} _(cite source filing in standard agentii citation format at runtime)_

#### Synergy Realization
- Revenue Synergies: {Quantified amount vs. target} _(cite source filing in standard agentii citation format at runtime)_
- Cost Synergies: {Quantified amount vs. target} _(cite source filing in standard agentii citation format at runtime)_
- Total Synergies: {$ realized YTD vs. full-year or cumulative target}

#### Financial Performance
- Revenue Contribution: {Acquired business revenue in quarter} _(cite source filing in standard agentii citation format at runtime)_
- Margin Impact: {Accretion/dilution to margins} _(cite source filing in standard agentii citation format at runtime)_
- EPS Impact: {Accretive/dilutive vs. guidance} _(cite source filing in standard agentii citation format at runtime)_

**Management Commentary**:
{Relevant quotes or summaries from earnings call} _(cite source filing in standard agentii citation format at runtime)_

**Analyst Perspective** (if available):
{Sell-side view on integration execution} _(cite source filing in standard agentii citation format at runtime)_

**Status Rationale**:
{Explanation of why this status was assigned based on evidence across dimensions}

{Repeat for each On-going/Unclear transaction}

**Overall Execution Assessment**:
- {Synthesize execution progress across all inorganic activities}
- {Note any patterns: most deals on track, specific areas of concern}
- {Highlight exceptional execution or significant challenges}
- {Assess management's overall M&A and integration capabilities}

<!-- END port-dimension-prompts methodology + modes -->

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

## Output File

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_growth-strategy_growth-drivers.md` .

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_growth-strategy_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `strategy-decomposition`, `capital-allocation`, `m-and-a-pipeline`, `geographic-expansion`). Examples:

- `LLY/2026-05-25_1430_growth-strategy_strategy-decomposition.md`
- `NVDA/2026-05-25_1545_growth-strategy_capital-allocation.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format **: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})`. Example: `[📄 LLY 10-K p.45](https://agentii.ai/v/LLY/sec175/45)`.

**agentii.md append **: After writing the output file, append a YAML block to `agentii.md` at the workspace root with `ticker`, `date`, `skill`, `output_file`, and `key_conclusions`. Create the file with a `# Project Memory Index` heading if it doesn't exist. See `contracts/agentii-md-schema.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
