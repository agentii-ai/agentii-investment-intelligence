---
name: earnings-sentiment
description: Earnings sentiment analysis, analyst estimates vs guidance, earnings surprise history, consensus sentiment, earnings revision trends, analyst rating changes, earnings beat miss track record, guidance accuracy, whisper numbers, pre-announcement sentiment
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
  - search_companies
  - search_xbrl_facts
  - search_documents
  - read_source_outline
  - read_source_pages
  - search_earnings_calendar
  - get_company_financials
  - get_company_profile
retrieval_scope: unstructured_document_search
min_tool_diversity: 8
---

<!-- analog: catalyst-calendar -->

## Preflight

!curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

**Ticker resolution (FR-082)**: Before any data retrieval, resolve the ticker via the three-layer fallback per retrieval.md Pre-Flight Step 0: (1) exact match via `search_companies(ticker=<input>)`, (2) pg_trgm fuzzy alias match via `gold.entity_aliases` (6,721 rows), (3) share class normalization for multi-class tickers (GOOG/GOOGL→GOOG, BRK.A/BRK.B→BRK.B). Return canonical ticker, match method, and confidence indicator.

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

<!-- BEGIN port-dimension-prompts methodology + modes -->

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill was upgraded from `structured_only` to `unstructured_document_search` scope per FR-084 (2026-06-03) to pull 8-K earnings press releases, MD&A guidance, and Item 1A risk factors alongside XBRL EPS data. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries spanning 8-K earnings press releases (management tone, sentiment language, guidance language), MD&A guidance discussion (forward-looking sentiment, confidence signals), and Item 1A risk factors (uncertainty context, cautionary language).
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist (FR-078c)**: prefer `?secondary_labels=financial_results_2_02,regulation_fd_disclosure_7_01` to capture earnings-related 8-Ks AND Reg-FD guidance disclosures before Layer 2. For uncertainty context, also query `?secondary_label=other_events_8_01` for material-event 8-Ks that may signal sentiment shifts.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Earnings sentiment: trailing 4 quarters for earnings-call tone and guidance trends

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared for this dimension.

### Protocol

This skill delivers analyst-grade output via 6 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.

### Mode: analyst-sentiment-assessment-current-quarter

**Display name**: analyst-sentiment-assessment-current-quarter

<!-- ported_from: references/prompts/7/7_1.yaml -->

**Focus**: Analyze sell-side preview reports to assess analyst sentiment and conviction level.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`

  - consistency_checks
  - evidence_requirements
  - sentiment_classification
- **structure**: ## Current-Quarter Analyst Sentiment Assessment

**Assessment Date**: {Current date}
**Upcoming Earnings Date**: {Next earnings date from fetch_stock_info}
**Analysis Period**: {30-day window before earnings}

**Data Sources Analyzed**:
- Morgan Stanley: {Report title and date if available, or "N/A"}
- Jefferies: {Report title and date if available, or "N/A"}

### Current-Quarter Estimates & Tone Summary

| **Key Financials** | **Expected Tone** | **Commentary / Notes** |
|:-------------------|:-----------------:|:-----------------------|
| Revenues | Highly Convicted / Positive / Negative / N/A | {Brief explanation with analyst quotes} _(cite source filing in standard agentii citation format at runtime)_ |
| EPS | Highly Convicted / Positive / Negative / N/A | {Brief explanation with analyst quotes} _(cite source filing in standard agentii citation format at runtime)_ |
| EBITDA | Highly Convicted / Positive / Negative / N/A | {Brief explanation with analyst quotes} _(cite source filing in standard agentii citation format at runtime)_ |
| **Adj. EBITDA** | Highly Convicted / Positive / Negative / N/A | {Brief explanation with analyst quotes} _(cite source filing in standard agentii citation format at runtime)_ |
| Net Income | Highly Convicted / Positive / Negative / N/A | {Brief explanation with analyst quotes} _(cite source filing in standard agentii citation format at runtime)_ |

**Overall Sentiment Summary**:
{2-3 sentence synthesis of overall analyst sentiment for upcoming quarter}

**Key Sentiment Drivers**:
- {List 2-3 main factors driving analyst conviction or concern}

### Mode: fy0-analyst-estimates-extraction

**Display name**: fy0-analyst-estimates-extraction

<!-- ported_from: references/prompts/7/7_2.yaml -->

**Focus**: Extract and calculate mean (average) analyst estimates for the current fiscal year (FY0).
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`

**Fiscal Year**: FY{year}
**Earnings Release Date**: {date}

**Data Sources**:
- Morgan Stanley: {title, date}
- Jefferies: {title, date}

| **Key Financials** | **Mean Estimate** | **Notes / Source Commentary** |
|:-------------------|:-----------------:|:-----------------------------|
| Revenues | <XXXM-amount> | Avg of MS: <XXXM-amount>, Jefferies: <XXXM-amount> _(cite source filing in standard agentii citation format at runtime)_ |
| EPS (Non-GAAP) | <X.XX-amount> | Avg of MS: <X.XX-amount>, Jefferies: <X.XX-amount> _(cite source filing in standard agentii citation format at runtime)_ |
| EBITDA | <XXXM-amount> | {or N/A if not disclosed} |
| **Adj. EBITDA** | <XXXM-amount> | {or N/A if not disclosed} |
| Net Income | <XXXM-amount> | {or N/A if not disclosed} |
| **Gross Margin** | XX.XX% | {or N/A if not disclosed} |
| **Operating Margin** | XX.XX% | {or N/A if not disclosed} |
| Net Margin | XX.XX% | {or N/A if not disclosed} |

**Calculation Notes**:
- Mean calculated as (MS estimate + Jefferies estimate) / 2
- If only one source available, use that single estimate
- All estimates rounded to appropriate precision

### Mode: current-quarter-fiscal-year-analyst-estimates

**Display name**: current-quarter-fiscal-year-analyst-estimates

<!-- ported_from: references/prompts/7/7_3_1.yaml -->

**Focus**: Extract and calculate mean analyst estimates from Morgan Stanley, Jefferies, and SEC filings.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`

**Current Quarter**: Q{X} {Year}
**Current Fiscal Year**: FY{Year}
**Earnings Release Date**: {date}

**Data Sources**:
- Morgan Stanley: {report title, date}
- Jefferies: {report title, date}
- SEC 8-K: {filing date if applicable, or N/A}

| **Key Financials** | **Current Quarter Estimate** | **Current Fiscal Year Estimate (FY0)** |
|:-------------------|:---------------------------:|:-------------------------------------:|
| Revenues | <XXXM-amount> | <XXXM-amount> |
| EPS (Non-GAAP) | <X.XX-amount> | <X.XX-amount> |
| EBITDA | <XXXM-amount> | <XXXM-amount> |
| **Adj. EBITDA** | <XXXM-amount> | <XXXM-amount> |
| Net Income | <XXXM-amount> | <XXXM-amount> |

**Sources and Calculations**:
- Revenues (Quarter): Mean of MS: <XXXM-amount>, Jefferies: <XXXM-amount> _(cite source filing in standard agentii citation format at runtime)_, _(cite source filing in standard agentii citation format at runtime)_
- Revenues (FY0): Mean of MS: <XXXM-amount>, Jefferies: <XXXM-amount> _(cite source filing in standard agentii citation format at runtime)_, _(cite source filing in standard agentii citation format at runtime)_
{Repeat for each metric}

**Notes**:
- All estimates represent analyst consensus as of {date}
- Estimates averaged across available sources
- N/A indicates metric not disclosed by any source

### Mode: management-guidance-extraction

**Display name**: management-guidance-extraction

<!-- ported_from: references/prompts/7/7_3_2.yaml -->

**Focus**: Extract management's official guidance for current quarter and fiscal year.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`

**Source Earnings Date**: {last earnings date}
**Current Quarter**: Q{X} {Year}
**Current Fiscal Year**: FY{Year}

**Data Sources**:
- SEC 8-K: {filing date}
- Earnings Presentation: {title, date if applicable}

| **Key Financials** | **Current Quarter Guidance** | **Current Fiscal Year Guidance (FY0)** |
|:-------------------|:---------------------------:|:-------------------------------------:|
| Revenues | <XXXM-amount> | <XXXM-amount> |
| EPS (Non-GAAP) | <X.XX-amount> | <X.XX-amount> |
| EBITDA | <XXXM-amount> | <XXXM-amount> |
| **Adj. EBITDA** | <XXXM-amount> | <XXXM-amount> |
| Net Income | <XXXM-amount> | <XXXM-amount> |

**Guidance Details**:
- Revenues (Quarter): {<XXX-amount>-XXXM range → midpoint <XXXM-amount>} _(cite source filing in standard agentii citation format at runtime)_
- Revenues (FY0): {<XXX-amount>-XXXM range → midpoint <XXXM-amount>} _(cite source filing in standard agentii citation format at runtime)_
{Repeat for each metric}

**Guidance Notes**:
- All values represent midpoint of ranges where applicable
- Guidance provided by management on {earnings date}
- N/A indicates no guidance provided for that metric

### Mode: current-quarter-estimates-vs-guidance

**Display name**: current-quarter-estimates-vs-guidance

<!-- ported_from: references/prompts/7/7_3_3.yaml -->

### Objective

Compile side-by-side comparison of analyst estimates and management guidance
for the CURRENT FISCAL QUARTER ahead of upcoming earnings release.

Calculate and present variance (delta) between analyst expectations and official guidance.

**Current Quarter**: Q{X} FY{Year}
**Upcoming Earnings Date**: {date}

**Data Sources**:
- Analyst Estimates: {MS and Jefferies previews with dates}
- Management Guidance: {8-K from last earnings, date}

| **Key Financials** | **Analyst Estimates** | **Management Guidance** | **Variance** | **% Var** |
|:-------------------|:---------------------:|:-----------------------:|:------------:|:---------:|
| Revenues | <XXXM-amount> | <XXXM-amount> | +<XXM-amount> | +X.X% |
| EPS (Non-GAAP) | <X.XX-amount> | <X.XX-amount> | +$0.XX | +X.X% |
| EBITDA | <XXXM-amount> | <XXXM-amount> | -<XXM-amount> | -X.X% |
| **Adj. EBITDA** | <XXXM-amount> | <XXXM-amount> | $0M | 0.0% |
| Net Income | <XXXM-amount> | <XXXM-amount> | +<XXM-amount> | +X.X% |

**Variance Analysis**:
- {Metric with largest positive variance}: Analysts {X}% above guidance
  - Potential drivers: {Brief explanation} _(cite source filing in standard agentii citation format at runtime)_
- {Metric with negative variance if any}: Analysts {X}% below guidance
  - Potential concerns: {Brief explanation} _(cite source filing in standard agentii citation format at runtime)_

**Overall Assessment**:
{2-3 sentences summarizing whether analysts are generally above, in-line, or below guidance,
and potential implications for upcoming earnings}

**Key Observations**:
- {Notable variance patterns}
- {Consistency or inconsistency across metrics}
- {Context for variances from preview reports}

- **variance_interpretation**:
  - in_line
  - material_variance
  - negative_variance
  - positive_variance

### Mode: full-year-estimates-vs-guidance

**Display name**: full-year-estimates-vs-guidance

<!-- ported_from: references/prompts/7/7_3_4.yaml -->

### Objective

Compile side-by-side comparison of analyst estimates and management guidance
for the CURRENT FISCAL YEAR (FY0).

Calculate variance to assess if analysts are above, in-line, or below guidance.

**Fiscal Year**: FY{Year} (ending {month/day/year})
**Data as of**: {current date}

**Data Sources**:
- Analyst Estimates (FY0): {MS and Jefferies previews, dates}
- Management Guidance (FY0): {8-K from last earnings, date}

| **Key Financials** | **Analyst Estimates** | **Management Guidance** | **Variance** | **% Var** |
|:-------------------|:---------------------:|:-----------------------:|:------------:|:---------:|
| Revenues | <XXXM-amount> | <XXXM-amount> | +<XXM-amount> | +X.X% |
| EPS (Non-GAAP) | <X.XX-amount> | <X.XX-amount> | +$0.XX | +X.X% |
| EBITDA | <XXXM-amount> | <XXXM-amount> | +<XXM-amount> | +X.X% |
| **Adj. EBITDA** | <XXXM-amount> | <XXXM-amount> | -<XXM-amount> | -X.X% |
| Net Income | <XXXM-amount> | <XXXM-amount> | $0M | 0.0% |

**Variance Analysis**:

### Metrics Above Guidance
{For each metric with +variance > 5%}:
- **{Metric}**: Analysts {X}% above guidance
  - Analyst rationale: {Key drivers from preview reports} _(cite source filing in standard agentii citation format at runtime)_
  - Implied upside: <XXM> or <X.XX> per share

### Metrics Below Guidance
{For each metric with -variance > 5%}:
- **{Metric}**: Analysts {X}% below guidance
  - Analyst concerns: {Key reasons from preview reports} _(cite source filing in standard agentii citation format at runtime)_
  - Potential downside: <XXM> or <X.XX> per share

### Metrics In-Line (±2%)
{List metrics with minimal variance}

**Overall Assessment**:
{Summary paragraph assessing whether analysts are generally constructive,
in-line, or cautious relative to management guidance. Discuss implications
for potential guidance revisions in upcoming earnings.}

**Strategic Implications**:
- **For Investors**: {What variance pattern suggests about potential outcomes}
- **Guidance Outlook**: {Likelihood of guidance raise/lower/maintain based on variance}
- **Key Drivers of Variance**: {Top 2-3 factors explaining estimate vs. guidance delta}

- **variance_significance**:
  - in_line
  - material
  - moderate

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

Write the final deliverable to `{{ticker}}/{{YYYY-MM-DD_HHMM}}_earnings-sentiment_analyst-sentiment.md` per FR-079.

## Output Structure

The final deliverable MUST be written as a markdown file to the workspace using the convention (FR-079):

```
{ticker}/{YYYY-MM-DD_HHMM}_earnings-sentiment_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `guidance-vs-estimates`, `analyst-tone`, `call-sentiment`, `surprise-bridge`). Examples:

- `LLY/2026-05-25_1430_earnings-sentiment_guidance-vs-estimates.md`
- `NVDA/2026-05-25_1545_earnings-sentiment_analyst-tone.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citation density**: ≥1 citation per 200 words. Bare `page_no` integers are forbidden — always use `{ticker} {citation_id} page<N>`. **Citation link format (FR-081)**: use clickable links: `[📄 {ticker} {form_type} p.{N}](https://www.agentii.ai/view?ticker={ticker}&citation_id={citation_id}&page_no={page<N>})`. Example: `[📄 LLY 8-K p.5](https://www.agentii.ai/view?ticker=LLY&citation_id=sec179&page_no=page5)`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
